
def argparse_with_banner(name, version, version_date):
    """
    Return an argparse.ArgumentParser instance with a help banner.
    """
    import argparse
    return argparse.ArgumentParser(
        description=f"""The 🌈Image auto✨ toolset
    
imgauto {name}
Created by LluisE (github.com/lluises)""",
        epilog=f"Version of imgauto {name}: {version} ({version_date})",
        formatter_class=argparse.RawTextHelpFormatter,
    )

