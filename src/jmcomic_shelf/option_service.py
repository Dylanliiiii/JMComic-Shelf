import os


def update_option_download_dir(option_path: str, download_dir: str) -> None:
    if not option_path or not os.path.exists(option_path):
        return
    if not download_dir:
        return

    from jmcomic import create_option

    option = create_option(option_path)
    option.dir_rule.base_dir = download_dir
    option.to_file(option_path)
