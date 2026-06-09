from services import access_control


def test_admin_password_authentication(monkeypatch):
    monkeypatch.setenv("APP_ADMIN_PASSWORD", "correct-horse-battery-staple")
    monkeypatch.setattr(access_control.st, "session_state", {})

    assert access_control.admin_access_is_configured()
    assert not access_control.authenticate_admin("incorrect")
    assert not access_control.is_admin()

    assert access_control.authenticate_admin("correct-horse-battery-staple")
    assert access_control.is_admin()

    access_control.sign_out_admin()
    assert not access_control.is_admin()


def test_missing_password_defaults_to_read_only(monkeypatch):
    monkeypatch.delenv("APP_ADMIN_PASSWORD", raising=False)
    monkeypatch.setattr(access_control.st, "session_state", {})
    monkeypatch.setattr(access_control.st, "secrets", {})

    assert not access_control.admin_access_is_configured()
    assert not access_control.authenticate_admin("")
    assert not access_control.is_admin()
