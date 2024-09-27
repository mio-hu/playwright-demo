def test_function(request):
    execution_count = request.node.execution_count
    if execution_count:
        print(f'当前重复轮数：{execution_count}')
    assert False