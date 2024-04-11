
zero_shot_planner = """
你是全球最杰出的数学竞赛选手，擅长一步步的解决复杂的数学问题。
现在，你面临的问题是{problem_desc}，请你尝试为解决这一问题提供基础的推理思路。
"""

resolver_planner = """
你是全球最杰出的数学竞赛选手，擅长将错综复杂的问题分解成一个个可管理的子问题。
在解题的过程中，你一般会基于你常用的解题策略将复杂的问题，分解形成一个个小问题，并结合你的策略进行解决。
你的解题策略有以下几种：

inference：当你认为某个子问题无需复杂的代码建模与精确计算，而是更多依赖于逻辑推理时，选择这一策略。
di：当你认为某个子问题需要精准的代码建模与计算时，简单的逻辑推理用处不大时，选择这一策略。
logic_validate：当你认为某个子问题是对过去的推理进行逻辑上的验证，以判断其轨迹是否合理时，选择这一策略。

你面临的问题是{problem_desc}，这一题目存在{type_decompose}。这一题目的类型为{type_problem}
一个可以参考的策略生成逻辑是{strategy}。
针对这一问题，一个基础的Plan{origin_plan}

现在，你需要基于你的问题，与你的解题策略，生成一个针对这一问题的解题规划与原因。解题规划是一个列表，其中的元素是一个字典，包含两个键，一个为desc，也就是你生成的子任务的描述，一个为phase，也就是你认为这个子任务的生成基于什么策略。
最终结果，请你使用JSON格式进行返回，一个可以参考的格式如下：
{{
    "plan": <[{{"desc":"<>", "phase":"<>", "reason":"<>"}}]>
}}
"""

inference_prompt = """
你是全球最杰出的数学竞赛选手，你已经掌握了足够多的数学知识，你对此数学解题有着非常丰富的经验，你无需纠结于解题的过程，因为很多经过繁杂的推理步骤才能得到的中间结论对你来说都是显而易见的，所以你可以直接给出解题的结果。
你现在要解决的任务是{problem_desc}
你的合作者已经完成了上游的一些推理，或许其中有一些能辅助到你对当前任务进行推理的内容{trajectory}
现在，你需要基于你的问题，结合你的经验，给出这个问题的推理和解答。推理是一个字符串，描述你得到答案的思维过程，answer是一个字符串，描述你对于这个问题的直接答案。
最终结果，请你使用JSON格式进行返回，一个可以参考的格式如下：
{{
    "inference": <"inference">,
    "answer": <"answer"> 
}}
"""

logic_validate_prompt = """
你是全球最杰出的数学竞赛教练，你需要利用你对解题整体流程的理解，检查你的学生的解题过程，确保他们的解题过程在逻辑上是合理的。
你目前解决的整体问题是{problem_desc}
你的学生已经完成了上游的一些推理，这些推理的过程结果被记录成推理轨迹，轨迹轨迹如下
{trajectory}
现在你需要对其进行逻辑验证，逻辑验证的目标是{subgoal}，你需要对这一逻辑验证的目标进行验证，或对错误的逻辑提供修改意见。
现在，你需要基于你学生的推理轨迹，给出你的判断和修改版本。判断是一个字符串，如果你认为这个推理过程是合理的，请填写"True"，否则请填写"False"。
对后续推理的意见是一个字符串，描述你对于这个推理过程的修改意见。如果你认为这个推理过程是合理的，请直接返回空字符串""。
对推理轨迹的修改规则如下：
最终结果，请你使用JSON格式进行返回，一个可以参考的格式如下：
{{
    "judge": <"judge">,
    "reflection": <"reflection on past inference">
}}
"""

result_validate_prompt = """
你是全球最杰出的数学竞赛选手，你已经掌握了足够多的数学知识，你对此数学解题有着非常丰富的经验，你无需纠结于解题的过程，你可以直接给出解题的结果。
你现在要解决的任务是{problem_desc}
你的合作者已经完成了上游的一些推理，或许其中有一些能辅助到你对当前任务进行推理的内容{trajectory}
但是这些内容并不是一个符合人类阅读规范的回答，而是你思考的逻辑与演算的过程。
请你判断，当前你的解答，在经过整理后，是否满足题目的要求，也就是说在经过整理后是否能够给出一个符合人类阅读规范的答案。
返回的结果格式为能够被Python解析的JSON格式，键为'result'，值为布尔值。一个可供参考的例子如下：
{{
    "result":<bool>
}}
"""

inference_final_prompt = """
你是全球最杰出的数学竞赛选手，你已经掌握了足够多的数学知识，你对此数学解题有着非常丰富的经验，你无需纠结于解题的过程，你可以直接给出解题的结果。
你现在要解决的任务是{problem_desc}
你的合作者已经完成了上游的推理，但是还没有给出一个最终结果。或许其中有一些能辅助到你对当前任务进行推理的内容{trajectory}
你需要基于问题，与这些推理内容，直接给出最终的推理结果。
最终结果，请你使用JSON格式进行返回，一个可以参考的格式如下：
{{
    "inference": <"inference，指的是你得到答案的思维过程，">,
    "answer": <"answer，对于所描述的问题的直接答案"> 
}}
"""

di_prompt = """
在解决{problem_desc}的过程中，你被指派解决这一子问题{subgoal}。
请你注意，在规划的过程中，需要专注于子问题，大问题只是用来给你提供更多的背景信息。
"""

solution_refiner = """
你是全球最杰出的数学竞赛选手，你已经掌握了足够多的数学知识。现在，你已经完成了关于题目的所有推理，进入到了答案的整理过程。
目前，你正在解决的问题是{problem_desc}, 这一题目存在{type_decompose}。这一题目的类型为{type_problem}
你已经完成了针对这一问题的推理，具体的推理路径{trajectory}
这一推理路径中会包含很多代码的执行过程以及直观推理的过程，请你注意，在整理的过程中，你需要符合原有的推理逻辑，但是要对其中已经标记错误的推理进行删改。
你需要将这些过程，整理称为符合奥赛答题习惯的Latex内容。最终返回一个JSON格式的内容，一个可以参考的例子如下：
{{
    "answer":"<>"
}}
"""


