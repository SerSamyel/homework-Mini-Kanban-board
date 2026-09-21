from fastapi import APIRouter

from ..models import Board, ColumnSummary
from ..store import store

router = APIRouter(tags=["board"])


@router.get("/board", response_model=Board, summary="Get the full board")
def get_board() -> Board:
    """Columns with their tasks, sorted by position. No auth — public."""
    return Board(columns=store.get_board())


@router.get(
    "/columns",
    response_model=list[ColumnSummary],
    summary="List columns (no tasks)",
)
def list_columns() -> list[ColumnSummary]:
    """Utility endpoint — columns are fixed/seeded, not editable in the MVP.
    No auth — public."""
    return [ColumnSummary(**c) for c in store.get_columns()]
