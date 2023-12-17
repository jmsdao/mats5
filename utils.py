import re
import numpy as np
import pandas as pd
import torch as t

from functools import partial
from typing import List, Optional, Union
from torch import Tensor


class HookedMistral:
    # See: https://github.com/huggingface/transformers/blob/main/src/transformers/models/mistral/modeling_mistral.py
    def __init__(self, hf_model, tokenizer):
        self.hf_model = hf_model
        self.tokenizer = tokenizer
        self.device = hf_model.device

    def __call__(self, prompts, attention_mask=None):
        if isinstance(prompts, list) and isinstance(prompts[0], str):
            tokens, attention_mask = self.to_tokens(prompts, return_mask=True)
            tokens = tokens.to(self.device)
            attention_mask = attention_mask.to(self.device)
        else:
            tokens = prompts
        out = self.hf_model(input_ids=tokens, attention_mask=attention_mask)
        return out.logits

    def to_tokens(self, prompts, device=None, return_mask=False):
        if device is None:
            device = self.device
        if isinstance(prompts, str):
            prompts = [prompts]
        tokens, attention_mask = self.tokenizer.batch_encode_plus(
            prompts,
            padding=True,
            return_tensors="pt",
        ).values()
        tokens = tokens.to(device)
        attention_mask = attention_mask.to(device)
        if return_mask:
            return tokens, attention_mask
        return tokens

    def to_string(self, tokens):
        if isinstance(tokens, t.Tensor) and tokens.dim() == 1:
            strings = self.tokenizer.decode(tokens)
        else:
            strings = self.tokenizer.batch_decode(tokens)
        return strings

    def to_string_tokenized(self, tokens):
        if isinstance(tokens, str) or (
            isinstance(tokens, list) and isinstance(tokens[0], str)
        ):
            tokens = self.to_tokens(tokens)[0]
        if isinstance(tokens, t.Tensor) and tokens.dim() == 1:
            return self.tokenizer.batch_decode(tokens)
        return [self.tokenizer.batch_decode(t) for t in tokens]

    def print_names(self, verbose=False):
        if verbose:
            for name, _ in self.hf_model.named_modules():
                print(name)
            return
        for name, _ in self.hf_model.named_modules():
            if name == "" or ("layers." in name and "layers.0" not in name):
                continue
            print(name.replace(".0", ".{0..31}"))

    def filter_names(self, callable):
        names = []
        for name, _ in self.hf_model.named_modules():
            if name == "":
                continue
            if callable(name):
                names.append(name)
        return names

    def get_resid_post_names(self, layers_filter=None):
        if isinstance(layers_filter, int):
            layers_filter = [layers_filter]
        if layers_filter is None:
            layers_filter = range(self.hf_model.config.num_hidden_layers)
        return [f"model.layers.{l}" for l in layers_filter]

    def get_component_names(self, layers_filter=None):
        if isinstance(layers_filter, int):
            layers_filter = [layers_filter]
        if layers_filter is None:
            layers_filter = range(self.hf_model.config.num_hidden_layers)
        names = []
        for l in layers_filter:
            names.append(f"model.layers.{l}.self_attn")
            names.append(f"model.layers.{l}.mlp")
        return names

    def get_module(self, name_to_get):
        for name, module in self.hf_model.named_modules():
            if name == name_to_get:
                return module
        raise Exception(f"{name_to_get} not found.")

    def add_hook(self, name, hook_fnc):
        module = self.get_module(name)
        handle = module.register_forward_hook(hook_fnc)
        return handle

    def reset_hooks(self):
        for module in self.hf_model.modules():
            module._forward_hooks.clear()

    def run_with_cache(self, prompts, names):
        # Cache and cache hook setup
        cache = {}

        def cache_hook(module, input, output, name="unknown"):
            if re.match(r"model\.layers\.\d+$", name):
                output = output[0]
            if re.match(r"model\.layers\.\d+\.self_attn$", name):
                output = output[0]
            cache[name] = output

        # Add hooks and forward pass
        handles = []
        for name in names:
            hook_fnc = partial(cache_hook, name=name)
            module = self.get_module(name)
            handles.append(module.register_forward_hook(hook_fnc))
        tokens, mask = self.to_tokens(prompts, return_mask=True)
        out = self.__call__(tokens, attention_mask=mask)

        # Remove cache hooks
        for handle in handles:
            handle.remove()

        return out, cache


def ntensor_to_long(
    tensor: Union[Tensor, np.ndarray],
    value_name: str = "values",
    dim_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Converts an n-dimensional tensor to a long format dataframe.
    """
    df = pd.DataFrame()
    if isinstance(tensor, Tensor):
        tensor = tensor.detach().cpu().numpy()
    df[value_name] = tensor.flatten()

    for i, _ in enumerate(tensor.shape):
        pattern = np.repeat(np.arange(tensor.shape[i]), np.prod(tensor.shape[i + 1 :]))
        n_repeats = int(np.prod(tensor.shape[:i]))
        df[f"dim{i}"] = np.tile(pattern, n_repeats)

    if dim_names is not None:
        df.columns = [value_name] + dim_names

    return df
