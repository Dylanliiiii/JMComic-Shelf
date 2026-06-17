def fetch_album_detail(option_path: str, jm_id: str):
    from jmcomic import create_option

    option = create_option(option_path)
    client = option.build_jm_client()
    return client.get_album_detail(jm_id)
