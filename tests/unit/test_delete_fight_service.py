import pytest

from app.services.fights import delete_fight_service

from .conftest import MockFightRepo


class TestDeleteFightService:
    def test_returns_none_success(self, mock_repo: MockFightRepo):
        mock_repo.delete.return_value = True
        result = delete_fight_service(1, mock_repo)
        assert result is None

    def test_calls_repo_with_id(self, mock_repo: MockFightRepo):
        mock_repo.delete.return_value = True
        delete_fight_service(1, mock_repo)
        mock_repo.delete.assert_called_once_with(1, mock_repo)

    def test_fails_if_not_found(self, mock_repo: MockFightRepo):
        mock_repo.delete.return_value = None
        with pytest.raises(ValueError, match="fight not found"):
            delete_fight_service(1, mock_repo)
