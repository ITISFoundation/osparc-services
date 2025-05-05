#!/usr/bin/env -S uv --quiet run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
# "jinja2", "pyyaml", "pydantic>2.0.0",
# "typer", "tqdm"
# ]
# ///
from pathlib import Path
import json
from typing import Any, Optional, Union, List
import typer
from pydantic import BaseModel, Field, validator
from jinja2 import Environment, FileSystemLoader, select_autoescape

app = typer.Typer(help="Docker Compose Parser and Template Generator")
from pathlib import Path
from typing import Any, Optional
import json
import typer
from pydantic import BaseModel, Field, field_validator
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

class NestedLabels(BaseModel):
    class Config:
        extra = "allow"

from pydantic import field_validator, ValidationInfo

class BuildConfig(BaseModel):
    context: str
    dockerfile: str
    target: str
    labels: dict[str, str]

    @field_validator('labels', mode='after')
    @classmethod
    def parse_json_labels(cls, labels: dict, info: ValidationInfo) -> dict:
        json_labels = [
            'io.simcore.key', 'io.simcore.version', 'io.simcore.type',
            'io.simcore.name', 'io.simcore.description', 'io.simcore.authors',
            'io.simcore.contact', 'io.simcore.inputs', 'io.simcore.outputs',
            'simcore.service.settings'
        ]
        
        parsed = {}
        for key, value in labels.items():
            if key in json_labels:
                try:
                    parsed[key] = json.loads(value)
                except json.JSONDecodeError:
                    parsed[key] = {"error": "Invalid JSON"}
            else:
                parsed[key] = value
        return parsed

class EnhancedService(BaseModel):
    image: str
    build: BuildConfig
    environment: dict[str, str] = Field(default={})
    ports: list[str]
    
    @field_validator('environment', mode='before')
    @classmethod
    def parse_environment(cls, v: list[str]) -> dict:
        return dict(item.split("=", 1) for item in v)

class EnhancedComposeSpecification(BaseModel):
    version: str
    services: dict[str, EnhancedService]

def render_template_(
    template_path: Path,
    compose_data: EnhancedComposeSpecification,
    service_name: str,desired_version: str,
    output_path: Optional[Path] = None,
) -> str:
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template(template_path.name)
    
    context = {
        "service": compose_data.services[service_name],
        "compose": compose_data,
        "desired_version": desired_version,
        "service_name": service_name
    }
    
    rendered = template.render(context)
    
    if output_path:
        output_path.write_text(rendered)
    return rendered

@app.command()
def render_template(
    template_path: Path = typer.Argument(..., exists=True),
    compose_path: Path = typer.Argument(..., exists=True),
    service_name: str = typer.Argument(...),
    desired_version: str = typer.Argument(..., help="Semantic version in format X.Y.Z"),
    output_path: Path = typer.Option(None),
):
    with compose_path.open() as f:
        raw_data = yaml.safe_load(f)
    compose_data = EnhancedComposeSpecification.model_validate(raw_data)
    if service_name not in compose_data.services:
        raise ValueError(f"Service '{service_name}' not found in compose file")
    
    result = render_template_(template_path, compose_data, service_name,desired_version, output_path)
    
    if not output_path:
        typer.echo(result)
            
if __name__ == "__main__":
    app()
