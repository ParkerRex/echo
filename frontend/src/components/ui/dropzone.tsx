import React, { useRef, useState } from "react";
import { cn } from "../../lib/utils";

interface DropZoneProps {
    onFilesAccepted: (files: FileList | File[]) => void;
    accept?: string;
    multiple?: boolean;
    className?: string;
    disabled?: boolean;
}

export const DropZone: React.FC<DropZoneProps> = ({
    onFilesAccepted,
    accept = ".mp4",
    multiple = false,
    className = "",
    disabled = false,
}) => {
    const [isDragging, setIsDragging] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        if (disabled) return;
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        if (disabled) return;
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        if (disabled) return;
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            onFilesAccepted(e.dataTransfer.files);
        }
    };

    const handleClick = () => {
        if (disabled) return;
        inputRef.current?.click();
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (disabled) return;
        if (e.target.files && e.target.files.length > 0) {
            onFilesAccepted(e.target.files);
        }
    };

    return (
        <div
            className={cn(
                "flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-8 cursor-pointer transition-colors",
                isDragging
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-300 bg-white hover:border-blue-400",
                className
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
            tabIndex={0}
            role="button"
            aria-label="Upload video files"
        >
            <input
                ref={inputRef}
                type="file"
                accept={accept}
                multiple={multiple}
                className="hidden"
                onChange={handleInputChange}
                tabIndex={-1}
            />
            <div className="flex flex-col items-center">
                <svg
                    className="w-12 h-12 text-blue-400 mb-2"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                    viewBox="0 0 48 48"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M24 6v24m0 0l-8-8m8 8l8-8M6 36h36"
                    />
                </svg>
                <span className="text-lg font-medium text-gray-700">
                    Drag & drop your <span className="text-blue-500">.mp4</span> file here
                </span>
                <span className="text-sm text-gray-500 mt-1">
                    or click to select from your computer
                </span>
            </div>
        </div>
    );
};

export default DropZone;
