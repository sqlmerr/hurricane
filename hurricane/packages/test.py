import hurricane


class TestPackage(hurricane.Package):
    name = "tester"
    developer = "@sqlmerr"
    version = hurricane.__version__

    async def on_load(self):
        # self.set("test", True)
        print(self.get("test"))
