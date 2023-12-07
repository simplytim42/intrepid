"""Main API file for Complex Frogs API."""

import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from complex_frogs.database import engine
from complex_frogs.database.models import ScrapeTargets
from complex_frogs.logger.config import LOGS_DIR, setup_logger
from complex_frogs.models.scraper import NewTarget, Target

setup_logger(LOGS_DIR / "api.log")

app = FastAPI()
session = Session(engine)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint for API."""
    logging.info("Root endpoint hit")
    return {"message": "Complex Frogs API"}


@app.get("/targets")
def get_targets() -> list[Target]:
    """Get all scraping targets from database."""
    try:
        logging.info("Getting targets from database")
        stmt = select(ScrapeTargets)
        targets = session.scalars(stmt)
    except SQLAlchemyError as e:
        logging.exception(msg=e)
        raise HTTPException(status_code=500, detail="Database error") from None
    else:
        return targets  # type: ignore[return-value]


@app.get("/targets/{target_id}")
def get_target(target_id: int) -> Target:
    """Get a single scraping target from database."""
    try:
        logging.info("Getting individual target from database")
        stmt = select(ScrapeTargets).where(ScrapeTargets.id == target_id)
        target = session.scalar(stmt)
    except SQLAlchemyError as e:
        logging.exception(msg=e)
        raise HTTPException(status_code=500, detail="Database error") from None
    else:
        if target is None:
            raise HTTPException(status_code=404, detail="Target not found")
        return target  # type: ignore[return-value]


@app.post("/targets")
def create_target(new_target: NewTarget) -> NewTarget:
    """Create a new scraping target in the database."""
    try:
        logging.info("Creating target in database")
        now = datetime.now(tz=timezone.utc)
        stmt = ScrapeTargets(
            site=new_target.site,
            sku=new_target.sku,
            send_notification=new_target.send_notification,
            date_added=now,
            last_scraped=datetime(1970, 1, 1, tzinfo=timezone.utc),
        )
        session.add(stmt)
        session.commit()
    except SQLAlchemyError as e:
        logging.exception(msg=e)
        raise HTTPException(status_code=500, detail="Database error") from None
    else:
        return new_target


@app.put("/targets/{target_id}")
def update_target(target_id: int, new_target: NewTarget) -> NewTarget:
    """Update a scraping target in the database."""
    try:
        logging.info("Updating target in database")
        target = get_target(target_id)
        target.site = new_target.site
        target.sku = new_target.sku
        target.send_notification = new_target.send_notification
        session.commit()
    except SQLAlchemyError as e:
        logging.exception(msg=e)
        raise HTTPException(status_code=500, detail="Database error") from None
    else:
        return new_target


session.close()
