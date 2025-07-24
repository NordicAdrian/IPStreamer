import click
from ip_streamer_nordic_adrian.ip_streamer import IPStreamer



@click.group()
def cli():
    pass


@cli.command()
@click.option("-s", "--stream", help="Video source (file path or webcam index).", default=0)
def run(stream):
    """Run the IPStreamer with the specified video source.
    STREAM can be a video file path or an integer for webcam.
    """
    ip_streamer = IPStreamer(stream)
    ip_streamer.run()
