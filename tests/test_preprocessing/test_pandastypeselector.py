import itertools as it

import numpy as np
import pandas as pd
import polars as pl
import pytest

from sklego.preprocessing import PandasTypeSelector
from tests.conftest import id_func


@pytest.mark.parametrize("transformer", [PandasTypeSelector(include=["number"])], ids=id_func)
@pytest.mark.parametrize("frame_func", [pd.DataFrame, pl.DataFrame])
def test_len_regression(transformer, random_xy_dataset_regr, frame_func):
    X, y = random_xy_dataset_regr
    X = frame_func(X)
    assert transformer.fit(X, y).transform(X).shape[0] == X.shape[0]


@pytest.mark.parametrize("transformer", [PandasTypeSelector(include=["number"])], ids=id_func)
@pytest.mark.parametrize("frame_func", [pd.DataFrame, pl.DataFrame])
def test_len_classification(transformer, random_xy_dataset_clf, frame_func):
    X, y = random_xy_dataset_clf
    X = frame_func(X)
    assert transformer.fit(X, y).transform(X).shape[0] == X.shape[0]


@pytest.mark.parametrize(
    "include,exclude",
    [_ for _ in it.combinations(["number", "datetime", "timedelta", "category", "datetimetz", None], 2)],
)
def test_get_params_str(include, exclude):
    transformer = PandasTypeSelector(include=include, exclude=exclude)

    assert transformer.get_params() == {"include": include, "exclude": exclude}


@pytest.mark.parametrize(
    "include,exclude",
    [_ for _ in it.combinations([np.int64, np.float64, np.datetime64, np.timedelta64], 2)],
)
def test_get_params_np(include, exclude):
    transformer = PandasTypeSelector(include=include, exclude=exclude)

    assert transformer.get_params() == {"include": include, "exclude": exclude}


@pytest.mark.parametrize("frame_func", [pd.DataFrame, pl.DataFrame])
def test_value_error_differrent_dtyes(frame_func):
    fit_df = frame_func({"a": [1, 2, 3], "b": [4, 5, 6]})
    transform_df = frame_func({"a": [4, 5, 6], "b": ["4", "5", "6"]})
    transformer = PandasTypeSelector(exclude=["category"]).fit(fit_df)

    with pytest.raises(ValueError):
        transformer.transform(transform_df)


@pytest.mark.parametrize("frame_func", [pd.DataFrame, pl.DataFrame])
def test_get_feature_names(frame_func):
    df = frame_func({"a": [4, 5, 6], "b": ["4", "5", "6"]})
    transformer_number = PandasTypeSelector(include="number").fit(df)
    assert transformer_number.get_feature_names() == ["a"]

    if frame_func is pd.DataFrame:
        transformer_number = PandasTypeSelector(include="object").fit(df)
    else:
        transformer_number = PandasTypeSelector(include="string").fit(df)
    assert transformer_number.get_feature_names() == ["b"]


def test_value_error_empty(random_xy_dataset_regr):
    transformer = PandasTypeSelector(exclude=["number"])
    X, y = random_xy_dataset_regr
    X = pd.DataFrame(X)

    with pytest.raises(ValueError):
        transformer.fit(X, y)


def test_value_error_inequal(random_xy_dataset_regr):
    transformer = PandasTypeSelector(include=["number"])
    X, y = random_xy_dataset_regr
    X = pd.DataFrame(X)
    if X.shape[0] > 0:
        with pytest.raises(ValueError):
            transformer.fit(X)
            # Remove column to create error
            transformer.transform(X.iloc[:, :-1])
