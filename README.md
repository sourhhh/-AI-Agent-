# AI Agent-Bug Detection and Repair-System
BIT软件体系结构与设计模式课程项目

基于AI Agent的软件项目缺陷自主检测与修复系统

一、项目介绍

1.项目内容

需要完成项目概况与缺陷梳理，包括对自有项目和Github开源项目的功能、技术栈以及存在的典型缺陷进行详细的梳理和分析。还要对开源项目的架构、设计模型及历史bugs进行分析，了解项目的整体结构和缺陷产生的原因。此外，要进行AI Agent架构设计、实现与功能开发，构建能够进行缺陷检测与修复的AI Agent系统。最后，对系统效果进行评估，并探索改进方向。

2.实验对象

本项目以“自有非平凡项目 + Github开源项目”作为实验对象，自有非平凡项目具有一定的复杂性和代表性，而Github开源项目则具有丰富的历史数据和广泛的社区支持。小组选择了小学期项目“智慧医疗管理系统”和github项目requests-cache作为研究对象。

二、项目设计

1.项目架构方案

本项目采用多Agent协作架构，具体包括感知Agent、决策Agent和执行Agent。
感知Agent负责读取项目信息，调用分析工具，提取缺陷特征，并输出结构化数据。决策Agent接收感知Agent输出的数据，判断缺陷的优先级，匹配处理策略，并下达执行指令。执行Agent接收决策Agent的指令，生成修复代码，进行替换测试，并反馈结果。

<img width="596" height="681" alt="架构设计图" src="https://github.com/user-attachments/assets/b7b98632-c3d2-455e-8739-216ef83915c4" />

2.工作流设计

<img width="1577" height="1457" alt="工作流设计" src="https://github.com/user-attachments/assets/8b9084d7-0c54-4eea-9045-d32d9933ea24" />
