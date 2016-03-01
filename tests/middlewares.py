dispatch_middleware = lambda r, d: lambda bulk_report=False: [1, 2, 3]
fetch_middleware = lambda r, f: lambda immediate_report=True: 1
