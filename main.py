import os
from modules.config_loader import load_config
from modules.gpt_module import GPTClient
from modules.pipeline_utils import load_pipe_with_loras
from modules.ad_generator import generate_ad_banner
from modules.logger import setup_logger

logger = setup_logger(__name__)

def main():
    try:
        logger.info("Loading config...")
        config = load_config()

        api_key = os.getenv(config["openai"]["api_key_env"])
        if not api_key:
            logger.error("OpenAI API key is not set in environment variables.")
            return

        logger.info("Initializing GPT client...")
        gpt_client = GPTClient(api_key=api_key, model_name=config["openai"]["gpt_model"])

        logger.info("Loading Stable Diffusion pipeline with LoRAs...")
        pipe = load_pipe_with_loras(config, "food")

        logger.info("Starting advertisement banner generation...")
        generate_ad_banner(config, gpt_client, pipe)
        logger.info("Advertisement banner generation finished successfully.")

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()
