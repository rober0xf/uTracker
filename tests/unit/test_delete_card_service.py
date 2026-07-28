import pytest

from app.services.cards import delete_card_service

from .conftest import MockCardRepo


class TestDeleteCardService:
    def test_returns_none_successfully(self, mock_repo: MockCardRepo):
        mock_repo.delete.return_value = True
        result = delete_card_service(1, mock_repo)
        assert result is None

    def test_calls_repo_with_id(self, mock_repo: MockCardRepo):
        mock_repo.delete.return_value = True
        delete_card_service(1, mock_repo)
        mock_repo.delete.assert_called_once_with(1)

    def test_fails_if_not_found(self, mock_repo: MockCardRepo):
        mock_repo.delete.return_value = None
        with pytest.raises(ValueError, match="card not found"):
            delete_card_service(1, mock_repo)

    def test_fails_if_false(self, mock_repo: MockCardRepo):
        mock_repo.delete.return_value = False
        with pytest.raises(ValueError, match="card not found"):
            delete_card_service(1, mock_repo)
