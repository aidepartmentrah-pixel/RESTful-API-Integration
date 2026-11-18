"""v1.1 maintenance: the real Directory path works next to the mock's own."""


def test_real_and_mock_paths_behave_the_same(client, auth_headers):
    for prefix in ("/api/directory/v1", "/his-general/api/directory/v1"):
        assert client.get(f"{prefix}/health").status_code == 200
        assert client.get(f"{prefix}/doctors", headers=auth_headers).status_code == 200
        assert client.get(f"{prefix}/doctors").status_code == 401
