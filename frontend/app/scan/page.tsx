"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import { CheckCircle2, ImageUp, Loader2, Play, RotateCcw, ScanLine } from "lucide-react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { ScanResult } from "@/types/scan";

type BarcodeDetectorResult = {
  rawValue?: string;
};

type BarcodeDetectorInstance = {
  detect(image: ImageBitmapSource): Promise<BarcodeDetectorResult[]>;
};

type BarcodeDetectorConstructor = new (options?: { formats?: string[] }) => BarcodeDetectorInstance;

type TextDetectorResult = {
  rawValue?: string;
  text?: string;
};

type TextDetectorInstance = {
  detect(image: ImageBitmapSource): Promise<TextDetectorResult[]>;
};

type TextDetectorConstructor = new () => TextDetectorInstance;

type DetectorWindow = Window &
  typeof globalThis & {
    BarcodeDetector?: BarcodeDetectorConstructor;
    TextDetector?: TextDetectorConstructor;
  };

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function uniqueLines(values: string[]) {
  return Array.from(new Set(values.map((value) => value.trim()).filter(Boolean))).join("\n");
}

async function detectTextFromImage(blob: Blob) {
  if (typeof window === "undefined" || typeof createImageBitmap === "undefined") {
    return "";
  }

  const detectorWindow = window as DetectorWindow;
  let bitmap: ImageBitmap | null = null;
  const values: string[] = [];

  try {
    bitmap = await createImageBitmap(blob);
  } catch {
    return "";
  }

  try {
    if (detectorWindow.BarcodeDetector) {
      const detector = new detectorWindow.BarcodeDetector();
      const barcodes = await detector.detect(bitmap).catch(() => []);
      values.push(...barcodes.map((barcode) => barcode.rawValue ?? ""));
    }

    if (detectorWindow.TextDetector) {
      const detector = new detectorWindow.TextDetector();
      const textBlocks = await detector.detect(bitmap).catch(() => []);
      values.push(...textBlocks.map((block) => block.rawValue ?? block.text ?? ""));
    }
  } finally {
    bitmap.close();
  }

  return uniqueLines(values);
}

function resultLabel(result: ScanResult | null) {
  if (!result) {
    return "No scan yet.";
  }
  if (result.scan_status === "CONFIRMED") {
    return "Scan confirmed.";
  }
  if (result.suggested_device_id) {
    return "Suggested device match found.";
  }
  if (result.detected_text) {
    return "Scan saved. No exact device match found.";
  }
  return "Scan saved. No label text was detected.";
}

export default function ScanPage() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const previewUrlRef = useRef<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [message, setMessage] = useState("Camera is ready.");
  const [labelText, setLabelText] = useState("");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, []);

  async function startCamera() {
    if (!navigator.mediaDevices?.getUserMedia) {
      setMessage("Camera access is not available in this browser.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => undefined);
      }
      setCameraActive(true);
      setMessage("Camera started.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Camera access failed.");
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    setMessage("Camera stopped.");
  }

  function updatePreview(blob: Blob) {
    const nextUrl = URL.createObjectURL(blob);
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    previewUrlRef.current = nextUrl;
    setPreviewUrl(nextUrl);
  }

  async function uploadScan(blob: Blob, fileName: string) {
    if (!getStoredToken()) {
      setMessage("Sign in first to scan inventory images.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      updatePreview(blob);
      const detectedText = await detectTextFromImage(blob);
      const combinedText = uniqueLines([labelText, detectedText]);
      if (detectedText) {
        setLabelText(combinedText);
      }

      const formData = new FormData();
      formData.append("file", blob, fileName);
      if (combinedText) {
        formData.append("detected_text", combinedText);
      }

      const response = (await apiFetch("/scan/image", {
        method: "POST",
        body: formData,
      })) as ScanResult;

      setResult(response);
      setMessage(resultLabel(response));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Scan upload failed.");
    } finally {
      setLoading(false);
    }
  }

  async function captureFrame() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !cameraActive) {
      setMessage("Start the camera first.");
      return;
    }

    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d");
    if (!context) {
      setMessage("Unable to capture the video frame.");
      return;
    }

    context.drawImage(video, 0, 0, width, height);
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.92));
    if (!blob) {
      setMessage("Unable to create the scan image.");
      return;
    }

    await uploadScan(blob, "webcam-scan.jpg");
  }

  async function uploadImage(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    await uploadScan(file, file.name || "uploaded-scan.jpg");
  }

  async function confirmSuggestedDevice() {
    if (!result?.id || !result.suggested_device_id) {
      return;
    }

    setConfirming(true);
    try {
      const response = (await apiFetch("/scan/confirm", {
        method: "POST",
        body: JSON.stringify({
          scan_id: result.id,
          device_id: result.suggested_device_id,
        }),
      })) as ScanResult;
      setResult(response);
      setMessage("Scan confirmed.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to confirm the scan.");
    } finally {
      setConfirming(false);
    }
  }

  return (
    <AppShell eyebrow="Scanner" title="Webcam detection" subtitle="Capture device labels and match them against the inventory device list.">
      <div className="grid gap-6 xl:grid-cols-[1.12fr_0.88fr]">
        <InfoCard title="Camera" description={message}>
          <div className="space-y-4">
            <div className="relative overflow-hidden rounded-[1.35rem] border border-white/10 bg-[#171716]">
              <video ref={videoRef} className="aspect-video w-full bg-[#11110f] object-cover" muted playsInline />
              {!cameraActive ? (
                <div className="absolute inset-0 grid place-items-center bg-[#171716]/86 text-center text-sm font-semibold text-[#bdb4a8]">
                  Camera paused
                </div>
              ) : null}
            </div>

            <canvas ref={canvasRef} className="hidden" />

            <div className="flex flex-wrap gap-3">
              <button className="inline-flex items-center gap-2 rounded-full bg-[#d9ff3f] px-5 py-3 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a]" onClick={startCamera} type="button">
                <Play className="h-4 w-4" />
                Start camera
              </button>
              <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-5 py-3 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45 disabled:cursor-not-allowed disabled:opacity-55" disabled={!cameraActive || loading} onClick={captureFrame} type="button">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ScanLine className="h-4 w-4" />}
                Capture and scan
              </button>
              <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-5 py-3 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45 disabled:cursor-not-allowed disabled:opacity-55" disabled={!cameraActive} onClick={stopCamera} type="button">
                <RotateCcw className="h-4 w-4" />
                Stop
              </button>
              <label className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-5 py-3 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45">
                <ImageUp className="h-4 w-4" />
                Upload image
                <input accept="image/*" capture="environment" className="hidden" onChange={uploadImage} type="file" />
              </label>
            </div>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-[#bdb4a8]">Label text</span>
              <textarea
                className="min-h-28 w-full resize-y rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-3 text-sm leading-6 text-white outline-none placeholder:text-[#6f675e] focus:border-[#d9ff3f]/60"
                onChange={(event) => setLabelText(event.target.value)}
                placeholder="Asset tag, serial number, barcode value"
                value={labelText}
              />
            </label>
          </div>
        </InfoCard>

        <InfoCard title="Detection result" description={resultLabel(result)}>
          <div className="space-y-4">
            {previewUrl ? (
              <img alt="Latest scan preview" className="max-h-72 w-full rounded-[1.15rem] border border-white/10 object-cover" src={previewUrl} />
            ) : (
              <div className="grid h-52 place-items-center rounded-[1.15rem] border border-dashed border-[#d9ff3f]/35 bg-[#171716] text-sm font-semibold text-[#9f968b]">
                No frame captured
              </div>
            )}

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Asset tag</p>
                <p className="mt-2 text-lg font-semibold text-white">{result?.detected_asset_tag ?? "-"}</p>
              </div>
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Serial</p>
                <p className="mt-2 text-lg font-semibold text-white">{result?.detected_serial_number ?? "-"}</p>
              </div>
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Model</p>
                <p className="mt-2 text-lg font-semibold text-white">{result?.detected_model ?? "-"}</p>
              </div>
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Confidence</p>
                <p className="mt-2 text-lg font-semibold text-white">{result ? `${Math.round(result.confidence_score * 100)}%` : "-"}</p>
              </div>
            </div>

            <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Suggested match</p>
              <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold text-white">{result?.suggested_display_name ?? "No match"}</p>
                  <p className="mt-1 text-sm text-[#bdb4a8]">
                    {result?.suggested_asset_tag ?? "-"}
                    {result?.suggested_score ? ` / ${Math.round(result.suggested_score)}% / ${result.suggested_reason}` : ""}
                  </p>
                </div>
                <button
                  className="inline-flex items-center gap-2 rounded-full bg-[#d9ff3f] px-5 py-3 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a] disabled:cursor-not-allowed disabled:opacity-55"
                  disabled={!result?.suggested_device_id || result.scan_status === "CONFIRMED" || confirming}
                  onClick={confirmSuggestedDevice}
                  type="button"
                >
                  {confirming ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                  Confirm
                </button>
              </div>
            </div>

            <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4 text-sm leading-6 text-[#bdb4a8]">
              <p>Status: <span className="text-white">{result?.scan_status ?? "-"}</span></p>
              <p>Created: <span className="text-white">{formatDate(result?.created_at)}</span></p>
              <p>Confirmed by: <span className="text-white">{result?.confirmed_by ?? "-"}</span></p>
              {result?.suggested_category ? <p>Match quality: <span className="text-white">{result.suggested_category}</span></p> : null}
            </div>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
