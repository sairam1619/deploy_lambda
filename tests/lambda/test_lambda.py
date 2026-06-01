import importlib
def test_lambda_handler_exists():
    module = importlib.import_module("src.lambda_code.app")
    assert hasattr(module, "lambda_handler")
    assert callable(module.lambda_handler)
