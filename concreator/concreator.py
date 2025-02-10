from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import logging
from stepchart_utils.chart_parser import Chart

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class Options:
    width: int
    height: int
    use_static_fade: bool = True,
    fade_duration: float = 0.5,
    duration: int = 15
    align_to_audio: bool = True,
    use_chart_sample_time: bool = True


def create_dynamic_banner(
        options: Options,
        chart: Chart, 
        output_dir: Path) -> Path:
    
    sm_file = chart.sm_file
    chart_dir = sm_file.filepath.parent
    
    # Look for a *.png or *.jpg in the chart directory
    banner_path = next(
        (p for p in chart_dir.iterdir() 
         if p.suffix.lower() in [".png", ".jpg"] 
         and "banner" in p.name.lower()),
        None
    )
    if not banner_path:
        banner_path = chart_dir / sm_file.banner if sm_file.banner else None

    background_path = chart_dir / sm_file.background if sm_file.background else None
    video_path = chart.video_file

    if not banner_path or not banner_path.exists() and background_path and background_path.exists():
        banner_path = background_path
    if banner_path.suffix == ".mp4":
        logger.warning(f"Banner path is already a video: {banner_path}")
        return banner_path
    
    output_dir = output_dir / sm_file.filepath.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)

    banner_output = output_dir / "banner.mp4"

    duration = options.duration
    if options.use_chart_sample_time:
        start_time = sm_file.sample_start
        if sm_file.sample_length:
            duration = sm_file.sample_length
    else:
        start_time = 0

    print(start_time)
    print(options.fade_duration)

    banner_cmd = None
    if options.use_static_fade:
        # FFmpeg command template for fade transition
        ffmpeg_template = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-framerate', '30',
            '-i', '{input_image}',     # Input static image
            '-ss', '{start_time}',  # Start time in seconds for video
            '-i', '{video_path}',      # Input video
            '-filter_complex',
            '[0:v]scale={width}:{height}:flags=lanczos,fps=30[v0];'
            '[1:v]scale={width}:{height}:flags=lanczos,fps=30[v1];'
            '[v0][v1]xfade=transition=fade:duration={fade_duration}:offset=1',
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            '-an',
            '-f', 'mp4',              
            '{output}'
        ]
        # Create banner video (typical ratio 418x164)
        banner_cmd = [arg.format(
            input_image=str(banner_path),
            start_time=str(start_time + options.fade_duration),
            video_path=str(video_path),
            width=options.width,
            height=options.height,
            fade_duration=options.fade_duration,
            output=f"{str(banner_output)}.temp"
        ) for arg in ffmpeg_template]

        logger.info(f"Creating banner video:\n{' '.join(banner_cmd)}")
        subprocess.run(banner_cmd, check=True)

        ffmpeg_thumbnail = [
            'ffmpeg', '-y',
            '-i', '{video_path}',      # Input video
            '-i', '{input_image}',     # Input static image
            '-map', '1',
            '-map', '0',
            '-c', 'copy',
            '-disposition:0', 'attached_pic',
            '{output}'
        ]
        thumbnail_cmd = [arg.format(
            video_path=f"{str(banner_output)}.temp",
            input_image=str(banner_path),
            output=str(banner_output)
        ) for arg in ffmpeg_thumbnail]

        logger.info(f"Creating banner thumbnail:\n{' '.join(thumbnail_cmd)}")
        subprocess.run(thumbnail_cmd, check=True)

        # Remove the temporary file
        os.remove(f"{str(banner_output)}.temp")

    else:
        # FFmpeg command template for direct video usage
        ffmpeg_template = [
            'ffmpeg', '-y',
            '-i', '{video_path}',      # Input video
            '-filter_complex',
            'scale={width}:{height}:flags=lanczos,fps=30',
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            '-an',
            '{output}'
        ]
        banner_cmd = [arg.format(
            video_path=str(video_path),
            width=options.width,
            height=options.height,
            output=str(banner_output)
        ) for arg in ffmpeg_template]

        logger.info(f"Creating banner video:\n{' '.join(banner_cmd)}")
        subprocess.run(banner_cmd, check=True)

    return banner_output


def create_dynamic_jacket(
        options: Options,
        chart: Chart, 
        output_dir: Path) -> Path:
    
    sm_file = chart.sm_file
    chart_dir = sm_file.filepath.parent

    # Look for a *.png or *.jpg in the chart directory
    jacket_path = next(
        (p for p in chart_dir.iterdir() 
         if p.suffix.lower() in [".png", ".jpg"] 
         and "jacket" in p.name.lower()),
        None
    )
    if not jacket_path:
         jacket_path = next(
        (p for p in chart_dir.iterdir() 
         if p.suffix.lower() in [".png", ".jpg"] 
         and "background" in p.name.lower()),
        None
    )   
    if not jacket_path:
        jacket_path = chart_dir / sm_file.jacket if sm_file.jacket else None

    background_path = chart_dir / sm_file.background if sm_file.background else None
    video_path = chart.video_file

    if not jacket_path or not jacket_path.exists() and background_path and background_path.exists():
        jacket_path = background_path

    if jacket_path.suffix == ".mp4":
        logger.warning(f"Jacket path is already a video: {jacket_path}")
        return jacket_path

    output_dir = output_dir / sm_file.filepath.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)

    jacket_output = output_dir / "jacket.mp4"

    duration = options.duration
    if options.use_chart_sample_time:
        start_time = sm_file.sample_start
        if sm_file.sample_length:
            duration = sm_file.sample_length
    else:
        start_time = 0

    if options.use_static_fade:
        # FFmpeg command template for fade transition
        ffmpeg_template = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-framerate', '30',
            '-i', '{input_image}',     # Input static image
            '-ss', '{start_time}',  # Start time in seconds for video
            '-i', '{video_path}',      # Input video
            '-filter_complex',
            '[0:v]scale={width}:{height}:flags=lanczos,fps=30[v0];'
            '[1:v]scale={width}:{height}:flags=lanczos,fps=30[v1];'
            '[v0][v1]xfade=transition=fade:duration={fade_duration}:offset=1',
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            '-an',
            '-f', 'mp4',
            '{output}'
        ]
        jacket_cmd = [arg.format(
            input_image=str(jacket_path),
            start_time=str(start_time + options.fade_duration),
            video_path=str(video_path),
            width=options.width,
            height=options.height,
            fade_duration=options.fade_duration,
            output=f"{str(jacket_output)}.temp"
        ) for arg in ffmpeg_template]

        # Execute FFmpeg commands
        logger.info(f"Creating jacket video:\n{' '.join(jacket_cmd)}")
        subprocess.run(jacket_cmd, check=True)

        ffmpeg_thumbnail = [
            'ffmpeg', '-y',
            '-i', '{video_path}',      # Input video
            '-i', '{input_image}',     # Input static image
            '-map', '1',
            '-map', '0',
            '-c', 'copy',
            '-disposition:0', 'attached_pic',
            '{output}'
        ]
        thumbnail_cmd = [arg.format(
            video_path=f"{str(jacket_output)}.temp",
            input_image=str(jacket_path),
            output=str(jacket_output)
        ) for arg in ffmpeg_thumbnail]

        logger.info(f"Creating jacket thumbnail:\n{' '.join(thumbnail_cmd)}")
        subprocess.run(thumbnail_cmd, check=True)

        # Remove the temporary file
        os.remove(f"{str(jacket_output)}.temp")

    else:
        # FFmpeg command template for direct video usage
        ffmpeg_template = [
            'ffmpeg', '-y',
            '-i', '{video_path}',      # Input video
            '-ss', str(start_time),  # Start time in seconds for video
            '-filter_complex', 
            'scale={width}:{height}:flags=lanczos,fps=30',
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            '-an',
            '{output}'
        ]
        jacket_cmd = [arg.format(
            video_path=str(video_path),
            width=options.width,
            height=options.height,
            output=str(jacket_output)
        ) for arg in ffmpeg_template]
        

        # Execute FFmpeg commands
        logger.info(f"Creating jacket video:\n{' '.join(jacket_cmd)}")
        subprocess.run(jacket_cmd, check=True)

    return jacket_output


def create_dynamic_assets(
        chart: Chart , 
        output_dir: Path, 
        use_static_fade: bool = True,
        create_jacket: bool = True,
        create_banner: bool = True) -> tuple[Path, Path]:
    """
    Creates dynamic video assets (jacket and banner) from an SMChart, video and background image.
    
    Args:
        chart: Chart object containing chart information
        output_dir: Directory to save the output files
        use_static_fade: If True, creates a fade transition from static image to video. 
                         If False, uses the video directly.
    
    Returns:
        tuple[Path, Path]: Paths to the generated jacket and banner videos
    """

    banner_output = None
    jacket_output = None
    if create_banner:
        banner_output = create_dynamic_banner(
            Options(
                use_static_fade=use_static_fade,
                width=418,
                height=164,
                fade_duration=0.5
            ),
            chart, 
            output_dir
        )
    if create_jacket:
        jacket_output = create_dynamic_jacket(
            Options(
                use_static_fade=use_static_fade,
                width=256,
                height=256,
                fade_duration=0.5
            ),
            chart, 
            output_dir
        )

    return jacket_output, banner_output
