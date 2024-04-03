# -*- coding: utf-8 -*-
# Date       : 2023/4/3
# Author     : @ Yi Huang @ Xin Cheng
# email      :
# Description: Solution Refiner Refine the results generated by the Math Resolver

from typing import Dict
from math_ai.codebase.llm.llm import OpenAILLM


class SolutionRefiner:
    def __init__(self):
        self.llm = OpenAILLM()
        self.role = "<TODO Here is Solution Refiner's system prompt>"
        self.llm.set_role(self.role)
    def run(self, problem: Dict) -> Dict:
        """
        Gate Controller choose human design strategy here
        and return strategy in dict
        you can add anything else such as problem's possible attention in dict.
        for example:
        {
            "strategy": "<content>",
            "attention": "<"Attention points identified during the determination of problem types.">"
        }
        """

        return {"strategy":"<content>"}


