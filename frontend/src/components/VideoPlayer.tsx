import { forwardRef, useImperativeHandle, useRef } from "react";

export interface VideoPlayerHandle {
  seekTo: (seconds: number) => void;
}

interface Props {
  videoUrl: string;
}

const VideoPlayer = forwardRef<VideoPlayerHandle, Props>(
  ({ videoUrl }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);

    useImperativeHandle(ref, () => ({
      seekTo(seconds: number) {
        const el = videoRef.current;
        if (!el) return;
        el.currentTime = seconds;
        el.pause();
      },
    }));

    return (
      <div className="rounded-xl overflow-hidden bg-black">
        <video
          ref={videoRef}
          src={videoUrl}
          controls
          className="w-full"
          playsInline
        >
          Your browser does not support the video tag.
        </video>
      </div>
    );
  }
);

VideoPlayer.displayName = "VideoPlayer";

export default VideoPlayer;
