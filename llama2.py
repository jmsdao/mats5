import torch
import transformer_lens.loading_from_pretrained as loading
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformer_lens import HookedTransformer


def load_model(use_runpod_cache=True, dtype=torch.float32, device="cpu"):
    cache_dir = "/workspace/cache/" if use_runpod_cache else None
    weights_source = "NousResearch/Llama-2-7b-hf"
    tlens_arch = "Llama-2-7b-hf"

    # Load the hf model into CPU
    tokenizer = AutoTokenizer.from_pretrained(weights_source, cache_dir=cache_dir)
    hf_model = AutoModelForCausalLM.from_pretrained(
        weights_source, torch_dtype=dtype, cache_dir=cache_dir
    )

    # Load the tlens model into device
    cfg = loading.get_pretrained_model_config(tlens_arch, dtype=dtype, device=device)
    tl_model = HookedTransformer(cfg, tokenizer=tokenizer)
    state_dict = loading.get_pretrained_state_dict(
        tlens_arch, cfg, hf_model=hf_model, dtype=dtype
    )
    tl_model.load_state_dict(state_dict, strict=False)

    return tl_model
