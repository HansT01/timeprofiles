if __name__ == "__main__":
    from timeprofiles import TimeProfileCollection as TPC
    from random import randint
    from time import sleep
    import concurrent.futures

    @TPC.profile_class_methods
    class ExampleClass:
        def method_a(self, num):
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                # Run method b as threads
                fs = (executor.submit(self.method_b) for _ in range(0, num))

                # Wait for all futures to complete
                for f in concurrent.futures.as_completed(fs):
                    pass

            self.method_d()

        def method_b(self):
            sleep(randint(0, 100) / 1000)
            self.method_c()

        def method_c(self):
            sleep(randint(0, 100) / 1000)

        def method_d(self):
            sleep(randint(0, 100) / 1000)

        @staticmethod
        def method_e():
            sleep(randint(0, 100) / 1000)

    example1 = ExampleClass()
    example1.method_a(5)

    TPC.display_profiles(TPC.ORDER_BY_NAME)
    TPC.plot_profiles()
