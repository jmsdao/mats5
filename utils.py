import numpy as np
import pandas as pd
from torch import Tensor
from typing import List, Optional, Union


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
        pattern = np.repeat(np.arange(tensor.shape[i]), np.prod(tensor.shape[i+1:]))
        n_repeats = int(np.prod(tensor.shape[:i]))
        df[f"dim{i}"] = np.tile(pattern, n_repeats)

    if dim_names is not None:
        df.columns = [value_name] + dim_names
    
    return df
