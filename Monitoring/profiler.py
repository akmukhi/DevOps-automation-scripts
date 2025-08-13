#Using fibanacci algorithm for the testing of the profiler
import sys
import os
import cProfile
import pstats
import io 
import argparse
import importlib.util
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
import psutil
import gc
import time

class PythonProfiler:
    #A profiling tool for python scripts
    def __init__(self, targetFile: str, outputFile: Optional[str] = None):
        self.targetFile = Path(targetFile)
        self.outputFile = outputFile
        self.profiler = cProfile.Profile()
        self.stats = None
        self.startTime = None 
        self.endTime = None
        self.memoryBefore = None
        self.memoryAfter = None
    def validateFile(self) -> bool:
        #Validate that the file exists
        if not self.targetFile.exists():
            print(f"ERROR: The file '{self.targetFile}' does not exist.")
            raise FileNotFoundError(f"The file '{self.targetFile}' does not exist.")
            return False
        if self.targetFile.suffix != '.py':
            print(f"ERROR: The file '{self.targetFile}' is not a Python file.")
            raise ValueError(f"The file '{self.targetFile}' is not a Python file.")
            return False
        return True
    
    #Get the current memory usage
    def getMemoryUsage(self) -> float:
        #Get the current memory
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def loadAndRunModule(self) -> bool:
        try:
            moduleName = self.targetFile.stem
            spec = importlib.util.spec_from_file_location(moduleName, self.targetFile)
            if spec is None:
                print(f"ERROR: Failed to load the module '{moduleName}'")
                return False
            module = importlib.util.module_from_spec(spec)
            self.memoryBefore = self.getMemoryUsage()
            self.startTime = time.time()
            self.profiler.enable()
            spec.loader.exec_module(module)
            self.profiler.disable()
            self.endTime = time.time()
            self.memoryAfter = self.getMemoryUsage()
            return True
        except Exception as e:
            print(f"ERROR: Execution failed: {e}")
            traceback.print_exc()
            return False
        
    def runFunction(self, functionName: str, *args, **kwargs) -> bool:
        #Running the function from the target
        try:
            #Loading the module
            spec = importlib.util.spec_from_file_location(self.targetFile.stem, self.targetFile)
            if spec is None or spec.loader is None:
                print(f"ERROR: Could not load module from '{self.targetFile}'")
                return False
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            #Getting the function
            if not hasattr(module, functionName):
                print(f"ERROR: Function '{functionName}' not found in module")
                return False
            func = getattr(module, functionName)

            #Record the memory
            self.memoryBefore = self.getMemoryUsage()

            #Start the profiling
            self.startTime = time.time()
            self.profiler.enable()
            result = func(*args, **kwargs)

            #Stop the profiler
            self.profiler.disable()
            self.endTime = time.time()
            self.memoryAfter = self.getMemoryUsage()

            print(f"Function '{functionName}' returned: {result}")
            return True
        except Exception as e:
            print(f"ERROR: Executing function '{functionName}': {e}")
            traceback.print_exc()
            return False
    
    def generateStats(self) -> None:
        #Generate the profiling statiscs
        if self.profiler is None:
            print("ERROR: No profiling data available")
            return
        
        #Create teh object to store stats
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats()
        self.stats = s.getvalue()
    
    def printSummary(self) -> None:
        #Print a summery of the results
        if not self.startTime or not self.endTime:
            print("ERROR: No execution data available")
            return
        executionTime = self.endTime - self.startTime
        memoryUsed = self.memoryAfter - self.memoryBefore if self.memoryBefore and self.memoryAfter else 0

        print("Summary")
        print("====================================")
        print(f"Target File: {self.targetFile}")
        print(f"Execution Time: {executionTime}")
        print(f"Memory Usage: {memoryUsed} MB")
        print(f"Peak Memory: {self.memoryAfter} MB")
        print("======================================")


    def printDetailedSummary(self, limit: int = 20) -> None:
        #Print the detailed statistics
        if not self.stats:
            self.generateStats()
        
        print("Detailed Statistics")
        print("==================================")

        #Split the stats
        lines = self.stats.split('\n')
        headerLines = lines[:6]
        dataLines = lines[6:-1]

        for line in headerLines:
            print(line)
        for line in dataLines[:limit]:
            print(line)
        
        if len(dataLines) > limit:
            print("\n")
            print(f"{len(dataLines) - limit} lines")
        print("==================================")

    def saveResults(self) -> None:
        #Save the results to a file
        if not self.outputFile:
            return
        try:
            with open(self.outputFile, 'w') as f:
                f.write(f"Python Profiler Results\n")
                f.write(f"Target File: {self.targetFile}\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("====================================================")
                f.write("\n")
                f.write("\n")

                if self.startTime and self.endTime:
                    executionTime = self.endTime - self.startTime
                    f.write(f"Execution Time: {executionTime:.3f} seconds\n")
                if self.memoryBefore and self.memoryAfter:
                    memoryUsed = self.memoryAfter - self.memoryBefore
                    f.write(f"Memory Usage: {memoryUsed:.2f} MB\n")
                    f.write(f"Peak Memory: {self.memoryAfter:.2f} MB\n")
                f.write("=====================================================")
                f.write("Detailed Statistics\n")
                f.write("=====================================================")

                if self.stats:
                    f.write(self.stats)
            print(f"Results saved to: {self.outputFile}")
        except Exception as e:
            print(f"ERROR: Saving results: {e}")
    
    def profile(self, functionName: Optional[str] = None, *args, **kwargs) -> bool:
        if not self.validateFile():
            return False
        print(f"Profiling: {self.targetFile}")

        gc.collect()
        success = False

        if functionName:
            print(f"Profiling Function: {functionName}")
            success = self.runFunction(functionName, *args, **kwargs)
        else:
            print("Profiling entire module")
            success = self.loadAndRunModule()
        if success:
            self.generateStats()
            self.printSummary()
            self.printDetailedSummary()
            self.saveResults()

        return success
    
    @staticmethod
    def main():
        #Main function to run the profiler from the terminal
        parser = argparse.ArgumentParser(
            description="Profiler - to profile python scripts for analysis"
        )

        parser.add_argument(
            "targetFile",
            help="Python file to profile"
        )

        parser.add_argument(
            "-o", "--output",
            help="Output file for the results"
        )

        parser.add_argument(
            "-f", "--function",
            help="Specific function to profile"
        )

        parser.add_argument(
            "-l", "--limit",
            type=int,
            default=20,
            help="Limit number of lines in output, default is 20"
        )

        args = parser.parse_args()
        profiler = PythonProfiler(args.targetFile, args.output)
        #Run the profile
        if args.function:
            success = profiler.profile(args.function)
        else:
            success = profiler.profile()
        
        if success:
            print("\nProfiling Done!")
        else:
            print("\nProfiling FAILED")
            sys.exit(1)
    
if __name__ == "__main__":
    PythonProfiler.main() 

