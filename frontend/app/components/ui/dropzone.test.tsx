/// <reference types="vitest" />
import { render, fireEvent, screen } from "@testing-library/react";
import { DropZone } from "./dropzone";
import { vi } from "vitest";

describe("DropZone", () => {
    it("renders the drop zone UI", () => {
        render(<DropZone onFilesAccepted={() => { }} />);
        // Use a function matcher to match text across element boundaries
        const dropZone = screen.getByRole("button", { name: /upload video files/i });
        expect(dropZone.textContent?.toLowerCase()).toContain("drag & drop your .mp4 file here");
        expect(dropZone.textContent?.toLowerCase()).toContain("or click to select from your computer");
    });

    it("calls onFilesAccepted when a file is dropped", () => {
        const handleFilesAccepted = vi.fn();
        render(<DropZone onFilesAccepted={handleFilesAccepted} />);
        const dropZone = screen.getByRole("button", { name: /upload video files/i });

        // Create a mock file
        const file = new File(["dummy content"], "test.mp4", { type: "video/mp4" });
        const dataTransfer = {
            files: [file],
            types: ["Files"],
            getData: vi.fn(),
            setData: vi.fn(),
            clearData: vi.fn(),
        };

        fireEvent.dragOver(dropZone, { dataTransfer });
        fireEvent.drop(dropZone, { dataTransfer });

        expect(handleFilesAccepted).toHaveBeenCalledWith([file]);
    });

    it("calls onFilesAccepted when a file is selected via input", () => {
        const handleFilesAccepted = vi.fn();
        render(<DropZone onFilesAccepted={handleFilesAccepted} />);
        const input = screen.getByLabelText(/upload video files/i).querySelector("input[type='file']") as HTMLInputElement;

        // Create a mock file list
        const file = new File(["dummy content"], "test.mp4", { type: "video/mp4" });
        Object.defineProperty(input, "files", {
            value: [file],
            writable: false,
        });

        fireEvent.change(input);

        expect(handleFilesAccepted).toHaveBeenCalledWith([file]);
    });
});
