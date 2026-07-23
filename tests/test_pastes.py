import asyncio
import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_create_and_read(client):
    res = await client.post("/api/pastes", json={
        "content": "print('hi')",
        "language": "python",
    })
    assert res.status_code == 201

    data = res.json()
    assert len(data["id"]) == 8

    raw = await client.get(f"/api/pastes/{data['id']}/raw")
    assert raw.status_code == 200
    assert raw.text == "print('hi')"


async def test_empty_content_rejected(client):
    res = await client.post("/api/pastes", json={"content": ""})
    assert res.status_code == 422


async def test_missing_paste_is_404(client):
    res = await client.get("/api/pastes/zzzzzzzz/raw")
    assert res.status_code == 404


async def test_delete_requires_correct_token(client):
    res = await client.post("/api/pastes", json={"content": "secret"})
    data = res.json()

    bad = await client.delete(f"/api/pastes/{data['id']}?token=wrong")
    assert bad.status_code == 404

    good = await client.delete(f"/api/pastes/{data['id']}?token={data['delete_token']}")
    assert good.status_code == 204


async def test_burn_after_read_serves_exactly_once(client):
    res = await client.post("/api/pastes", json={
        "content": "burn me",
        "burn_after_read": True,
    })
    paste_id = res.json()["id"]

    results = await asyncio.gather(*[
        client.get(f"/{paste_id}") for _ in range(10)
    ])

    successes = [r for r in results if r.status_code == 200]
    assert len(successes) == 1