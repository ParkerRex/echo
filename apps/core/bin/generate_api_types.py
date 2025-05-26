#!/usr/bin/env python3
"""
Generate TypeScript types from Pydantic API schemas.

This script extracts all Pydantic models from our API schemas and generates
corresponding TypeScript interfaces for frontend consumption.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps" / "core"))

try:
    from pydantic import BaseModel

    from apps.core.api.schemas.video_processing_schemas import (
        SignedUploadUrlResponse,
        VideoDetailsResponse,
        VideoJobResponseSchema,
        VideoJobSchema,
        VideoJobWithDetailsResponseSchema,
        VideoMetadataResponseSchema,
        VideoMetadataSchema,
        VideoMetadataUpdateRequestSchema,
        VideoResponseSchema,
        VideoSchema,
        VideoSummary,
        VideoSummarySchema,
        VideoUploadResponseSchema,
        VideoWithJobsResponseSchema,
    )
    from apps.core.models.enums import ProcessingStatus
except ImportError as e:
    print(f"Error importing schemas: {e}")
    print(
        "Make sure you're running this from the project root and dependencies are installed"
    )
    sys.exit(1)


def pydantic_to_typescript_type(python_type: str) -> str:
    """Convert Python type annotations to TypeScript types."""
    type_mapping = {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "datetime": "string",  # ISO string
        "Optional[str]": "string | null",
        "Optional[int]": "number | null",
        "Optional[float]": "number | null",
        "Optional[bool]": "boolean | null",
        "Optional[datetime]": "string | null",
        "List[str]": "string[]",
        "List[int]": "number[]",
        "Dict[str, str]": "Record<string, string>",
        "Dict[str, Any]": "Record<string, any>",
        "Optional[List[str]]": "string[] | null",
        "Optional[Dict[str, str]]": "Record<string, string> | null",
        "Optional[Dict[str, Any]]": "Record<string, any> | null",
    }
    return type_mapping.get(python_type, "any")


def generate_enum_typescript(enum_class) -> str:
    """Generate TypeScript enum from Python enum."""
    enum_name = enum_class.__name__
    values = [f'  {member.name} = "{member.value}"' for member in enum_class]
    return f"export enum {enum_name} {{\n{',\n'.join(values)}\n}}"


def generate_interface_typescript(model_class: BaseModel, interface_name: str) -> str:
    """Generate TypeScript interface from Pydantic model."""
    try:
        # Get the JSON schema from the model
        schema = model_class.model_json_schema()
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        fields = []
        for field_name, field_info in properties.items():
            field_type = convert_json_schema_type_to_typescript(field_info)
            optional_marker = "" if field_name in required else "?"
            fields.append(f"  {field_name}{optional_marker}: {field_type};")

        interface_body = "\n".join(fields)
        return f"export interface {interface_name} {{\n{interface_body}\n}}"
    except Exception as e:
        print(f"Error generating interface for {interface_name}: {e}")
        return f"// Error generating interface for {interface_name}: {e}"


def convert_json_schema_type_to_typescript(field_info: Dict[str, Any]) -> str:
    """Convert JSON schema field info to TypeScript type."""
    # Handle case where field_info might be a boolean or other non-dict type
    if not isinstance(field_info, dict):
        return "any"

    field_type = field_info.get("type")

    if field_type == "string":
        # Check for enum
        if "enum" in field_info:
            return " | ".join(f'"{value}"' for value in field_info["enum"])
        # Check for format (like datetime)
        if field_info.get("format") == "date-time":
            return "string"  # ISO date string
        return "string"
    elif field_type == "integer":
        return "number"
    elif field_type == "number":
        return "number"
    elif field_type == "boolean":
        return "boolean"
    elif field_type == "array":
        items = field_info.get("items", {})
        item_type = convert_json_schema_type_to_typescript(items)
        return f"{item_type}[]"
    elif field_type == "object":
        # Check if it's a Record type
        additional_properties = field_info.get("additionalProperties")
        if additional_properties:
            value_type = convert_json_schema_type_to_typescript(additional_properties)
            return f"Record<string, {value_type}>"
        return "Record<string, any>"
    elif field_type is None and "anyOf" in field_info:
        # Handle Union types (like Optional fields)
        types = []
        for option in field_info["anyOf"]:
            if not isinstance(option, dict):
                continue
            if option.get("type") == "null":
                continue  # We'll add null at the end
            types.append(convert_json_schema_type_to_typescript(option))

        # Check if null is allowed
        has_null = any(
            isinstance(option, dict) and option.get("type") == "null"
            for option in field_info["anyOf"]
        )
        type_str = " | ".join(types) if types else "any"

        if has_null:
            type_str += " | null"

        return type_str
    elif "$ref" in field_info:
        # Handle references to other schemas
        ref = field_info["$ref"]
        # Extract the model name from the reference
        model_name = ref.split("/")[-1]
        return model_name
    else:
        return "any"


def main():
    """Generate TypeScript types from Pydantic schemas."""

    # Define the schemas to export
    schemas = [
        (VideoResponseSchema, "VideoResponse"),
        (VideoJobResponseSchema, "VideoJobResponse"),
        (VideoMetadataResponseSchema, "VideoMetadataResponse"),
        (VideoSummarySchema, "VideoSummary"),
        (VideoUploadResponseSchema, "VideoUploadResponse"),
        (VideoWithJobsResponseSchema, "VideoWithJobsResponse"),
        (VideoJobWithDetailsResponseSchema, "VideoJobWithDetailsResponse"),
        (VideoMetadataUpdateRequestSchema, "VideoMetadataUpdateRequest"),
        (SignedUploadUrlResponse, "SignedUploadUrlResponse"),
        (VideoSummary, "VideoSummaryLegacy"),  # Avoid naming conflict
        (VideoSchema, "Video"),
        (VideoMetadataSchema, "VideoMetadata"),
        (VideoJobSchema, "VideoJob"),
        (VideoDetailsResponse, "VideoDetailsResponse"),
    ]

    # Generate TypeScript content
    typescript_content = []

    # Add header comment
    typescript_content.append("""/**
 * Auto-generated TypeScript types from Pydantic API schemas.
 * 
 * DO NOT EDIT THIS FILE MANUALLY!
 * 
 * This file is generated by apps/core/bin/generate_api_types.py
 * Run `pnpm codegen:api-types` to regenerate.
 */

""")

    # Generate ProcessingStatus enum
    typescript_content.append(generate_enum_typescript(ProcessingStatus))
    typescript_content.append("")

    # Generate interfaces
    for schema_class, interface_name in schemas:
        interface_ts = generate_interface_typescript(schema_class, interface_name)
        typescript_content.append(interface_ts)
        typescript_content.append("")

    # Write to output file
    output_dir = project_root / "apps" / "web" / "app" / "types"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "api.ts"

    with open(output_file, "w") as f:
        f.write("\n".join(typescript_content))

    print(f"✅ TypeScript types generated successfully: {output_file}")
    print(f"📝 Generated {len(schemas)} interfaces and 1 enum")


if __name__ == "__main__":
    main()
