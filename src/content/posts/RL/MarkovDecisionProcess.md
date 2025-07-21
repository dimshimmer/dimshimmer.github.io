---
title: Markov Decision Process
published: 2025-07-21
tags: [Machine Learning, Statistics, AI]
category: RL
draft: false
---

Markov Decision Process (MDP) almost defines the standard format of the reinforcement learning. With the symbolic representation, almost any problem can be transfered to the MDP. Learning the reinforcement, MDP is the best start. 

# Definition of Reinforcement Learning

The direct neural network training process, always feeds the data to the model directly. The target is to improve its perceptibility (like CNN) instead of the decision-making capability. The Reinforcement Learning (RL) showed up to make the agent learn from the feedback from the enviroment. With the reward from the enviroment, the dicision made by the agent can gradually meet the human's expectation. In machine learning area, with a trainable agent, we hope it can find the optimal strategies to the certain decision problem. 

Formulaically, all the reinforcement learning can be seen as a MDP. The solution to such scenario, is also the solution of the RL. 

# Markov Decision Process

Formally, a MDP is a 4-tuple ($S,A,P_a, R_a$), where:

- $S$: the state space. 
- $A$: the action space ($A_s$ is the set of available actions from state $s$)
- $P_a(s,s')$: the paobability that action $a$ in state $s$ at time $t$ will lead to state $s'$ at time $t+1$. Generally:$Pr(s_{t+1}\in S' | s_t = s, a_t=a) = \int _{S'} P_a(s,s')ds'$, for every $S'\sube S$. 
- $R_a(s,s')$: immediate reward received after transitioning from state $s$ to state $s'$. 

Usually, the optimization objective of MDP is to find a good policy for the decision maker. Thus, there exsists a policy function $\pi$, a (potentially probabilistic) mapping from $S$ to $A$. Combined with the MDP, the policy fixes the resulting combination behaves. The objective is to choose a policy $\pi$, maximizes some cumulative function of the random rewards:

$$
E_{a_t \sim \pi (s_t), s_{t+1} \sim P_{a_t}(s_t,s_{t+1})}\big[\sum ^{\infty} _{t=0} \gamma^t R_{a_t}(s_t,s_{t+1}) \big],
$$

where $\gamma$ is the discount factor satisfying  $0\leq \gamma  \leq \ 1$, which is usually close to 1 (for example,  $\gamma =1/(1+r)$ for some discount rate $r$). A lower discount factor motivates the decision maker to favor taking actions early, rather than postpone them indefinitely[^1].

[^1]: [wiki/Markov_decision_process](https://en.wikipedia.org/wiki/Markov_decision_process).