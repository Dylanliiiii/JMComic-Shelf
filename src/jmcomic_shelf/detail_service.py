import os


def fetch_album_detail(option_path: str, jm_id: str):
    from jmcomic import create_option

    if not option_path:
        raise ValueError('请先在设置里选择配置文件 jmcomic-option.yml')
    if not os.path.exists(option_path):
        raise FileNotFoundError(f'配置文件不存在: {option_path}')

    option = create_option(option_path)
    client = option.build_jm_client()
    return client.get_album_detail(jm_id)
