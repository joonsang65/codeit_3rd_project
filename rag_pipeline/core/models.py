# /rag_pipeline/core/models.py.
import accelerate, torch
from transformers import pipeline
from omnigen2.pipelines.omnigen2.pipeline_omnigen2 import OmniGen2Pipeline
from omnigen2.models.transformers.transformer_omnigen2 import OmniGen2Transformer2DModel
from omnigen2.pipelines.omnigen2.pipeline_omnigen2_chat import OmniGen2ChatPipeline
# 호스트 경로.
from rag_pipeline.utils.timing_utils import timing_decorator

@timing_decorator
def initialize_pipelines(model_path: str, hf_token: str, accelerator: accelerate.Accelerator):
    """Initializes and returns the OmniGen2 diffusion and chat pipelines."""
    diffusion_pipeline = OmniGen2Pipeline.from_pretrained(
        model_path,
        torch_dtype = torch.bfloat16,
        trust_remote_code = True,
        token = hf_token,
    )
    diffusion_pipeline.transformer = OmniGen2Transformer2DModel.from_pretrained(
        model_path,
        subfolder = "transformer",
        torch_dtype = torch.bfloat16,
    )
    diffusion_pipeline = diffusion_pipeline.to(accelerator.device, dtype = torch.bfloat16)

    chat_pipeline = OmniGen2ChatPipeline.from_pipe(pipeline = diffusion_pipeline, transformer = diffusion_pipeline.transformer)

    return diffusion_pipeline, chat_pipeline
