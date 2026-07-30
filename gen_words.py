#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 B2/C1 英语学习词库（面向口语沟通）
输出：可直接粘贴进 index.html 的 JS 数组文本
字段：{w, pos, cn, ex, zh}  —— 不写音标(ph)，因为卡片不渲染、发音走 Web Speech
策略：
  1. CORE：手工精校的核心词，含自然例句与准确中文翻译
  2. BULK：按主题批量扩展，例句用 POS 感知模板生成（语法正确、中文对应）
"""
import json, re, random
from eng_to_ipa import convert as ipa
import wordbank1, wordbank2, wordbank3, wordbank4, wordbank5

# ---------------- 1. 核心精校词（自然例句 + 准确中文） ----------------
CORE = [
 ("articulate","v.","清晰表达","She articulated her thoughts clearly.","她清晰地表达了想法。"),
 ("elaborate","v.","详细说明","Can you elaborate on that?","你能详细说说吗？"),
 ("emphasize","v.","强调","I'd like to emphasize this point.","我想强调这一点。"),
 ("clarify","v.","澄清","Let me clarify what I mean.","让我澄清一下我的意思。"),
 ("contradict","v.","反驳；矛盾","That contradicts what you said.","这跟你说的矛盾。"),
 ("justify","v.","证明…合理","How can you justify that?","你怎么证明那是对的？"),
 ("acknowledge","v.","承认","I acknowledge your concern.","我承认你的担忧有道理。"),
 ("persuade","v.","说服","I couldn't persuade him.","我没法说服他。"),
 ("compromise","v./n.","妥协；折中","We need to compromise.","我们需要各退一步。"),
 ("frustrated","adj.","挫败的；沮丧的","I feel frustrated with the progress.","我对进展感到挫败。"),
 ("overwhelmed","adj.","不知所措的","I'm overwhelmed by work.","工作多得让我喘不过气。"),
 ("resentful","adj.","怨恨的","Don't be resentful about it.","别对此耿耿于怀。"),
 ("sympathetic","adj.","同情的","She was very sympathetic.","她很能共情。"),
 ("indifferent","adj.","漠不关心的","I'm not indifferent to this.","我不是不在乎这个。"),
 ("enthusiastic","adj.","热情的","He's enthusiastic about the plan.","他对计划充满热情。"),
 ("skeptical","adj.","怀疑的","I'm skeptical about his story.","我对他的说法持怀疑态度。"),
 ("genuine","adj.","真诚的","Her apology felt genuine.","她的道歉感觉很真诚。"),
 ("reluctant","adj.","不情愿的","He was reluctant to agree.","他不情愿地同意了。"),
 ("content","adj.","满足的","I'm content with my life.","我对生活感到满足。"),
 ("collaborate","v.","合作","We collaborate closely.","我们紧密合作。"),
 ("delegate","v.","委派；授权","I'll delegate this task.","我会把这个任务分派出去。"),
 ("prioritize","v.","优先处理","We need to prioritize.","我们需要排个优先级。"),
 ("negotiate","v.","谈判","Let's negotiate the terms.","我们来谈一下条款。"),
 ("evaluate","v.","评估","Please evaluate the situation.","请评估一下情况。"),
 ("implement","v.","实施","We'll implement next week.","我们下周开始实施。"),
 ("supervise","v.","监督","She supervises the team.","她负责监管团队。"),
 ("recruit","v.","招聘","We're recruiting new staff.","我们在招新人。"),
 ("resign","v.","辞职","He resigned last week.","他上周辞职了。"),
 ("promote","v.","晋升；推广","She got promoted to manager.","她升职做了经理。"),
 ("bond","n./v.","纽带；建立关系","We have a strong bond.","我们有很强的感情纽带。"),
 ("conflict","n./v.","冲突","We had a conflict of interest.","我们有利益冲突。"),
 ("reconcile","v.","和解","They finally reconciled.","他们终于和好了。"),
 ("intimacy","n.","亲密","Intimacy takes time to build.","亲密关系需要时间培养。"),
 ("manipulate","v.","操纵","Don't manipulate people.","不要操纵别人。"),
 ("supportive","adj.","支持的","He's been very supportive.","他一直很支持我。"),
 ("judgmental","adj.","爱评判的","Don't be so judgmental.","别那么爱评头论足。"),
 ("compatible","adj.","合得来的","Are we compatible?","我们合适吗？"),
 ("distant","adj.","疏远的","She's been distant lately.","她最近有点疏远。"),
 ("appreciate","v.","感激；欣赏","I really appreciate your help.","我真的非常感谢你的帮助。"),
 ("perspective","n.","视角；观点","From my perspective...","从我的角度来看……"),
 ("circumstance","n.","情况；境遇","Under these circumstances...","在这种情况下……"),
 ("consequence","n.","后果","Consider the consequences.","考虑一下后果。"),
 ("tendency","n.","倾向","She has a tendency to worry.","她容易焦虑。"),
 ("phenomenon","n.","现象","It's a common phenomenon.","这是一个常见现象。"),
 ("criterion","n.","标准","What's your criterion?","你的标准是什么？"),
 ("assumption","n.","假设","That's a wrong assumption.","那是个错误的假设。"),
 ("concept","n.","概念","It's a difficult concept.","这是个难懂的概念。"),
 ("principle","n.","原则","Stick to your principles.","坚持你的原则。"),
 ("evidence","n.","证据","Where's the evidence?","证据在哪？"),
 ("accommodate","v.","容纳；迁就","Can you accommodate us?","能安排一下吗？"),
 ("maintain","v.","维持","Maintain a healthy lifestyle.","保持健康的生活方式。"),
 ("consume","v.","消耗；消费","We consume too much sugar.","我们糖吃太多了。"),
 ("acquire","v.","获得","She acquired new skills.","她学到了新技能。"),
 ("dispose","v.","处理（掉）","How do I dispose of this?","这个怎么处理？"),
 ("substitute","v./n.","替代品；代替","Is there a substitute?","有替代的吗？"),
 ("adjust","v.","调整；适应","I need time to adjust.","我需要时间适应。"),
 ("operate","v.","操作；运转","How does this operate?","这个怎么操作？"),
 ("function","n./v.","功能；运行","What's its function?","它的功能是什么？"),
 ("procedure","n.","流程","Follow the procedure.","按流程来。"),
 ("symptom","n.","症状","What are the symptoms?","有什么症状？"),
 ("therapy","n.","治疗","She started therapy.","她开始做心理治疗了。"),
 ("anxiety","n.","焦虑","I struggle with anxiety.","我在和焦虑作斗争。"),
 ("depression","n.","抑郁","Depression is treatable.","抑郁症是可以治疗的。"),
 ("insomnia","n.","失眠","I suffer from insomnia.","我有失眠症。"),
 ("nutrition","n.","营养","Pay attention to nutrition.","注意营养均衡。"),
 ("medication","n.","药物","Take your medication on time.","按时吃药。"),
 ("recover","v.","恢复","It takes time to recover.","恢复需要时间。"),
 ("chronic","adj.","慢性的","I have chronic back pain.","我有慢性背痛。"),
 ("mental","adj.","心理的","Mental health matters.","心理健康很重要。"),
 ("budget","n./v.","预算","Stick to your budget.","控制好预算。"),
 ("invest","v.","投资","I invest in stocks.","我投资股票。"),
 ("expense","n.","开支","Cut down expenses.","削减开支。"),
 ("affordable","adj.","负担得起的","It's quite affordable.","这个价格还算实惠。"),
 ("luxury","n.","奢侈品","It's a luxury item.","这是奢侈品。"),
 ("discount","n.","折扣","Any discount available?","有折扣吗？"),
 ("installment","n.","分期付款","Pay in installments.","分期付款吧。"),
 ("transaction","n.","交易","The transaction failed.","交易失败了。"),
 ("profit","n.","利润","The profit margin is low.","利润率很低。"),
 ("economical","adj.","经济的；省钱的","This car is economical.","这车很省油。"),
 ("destination","n.","目的地","What's our destination?","我们的目的地是哪？"),
 ("itinerary","n.","行程安排","Check the itinerary.","看一下行程表。"),
 ("accommodation","n.","住宿","Book accommodation in advance.","提前订住宿。"),
 ("scenic","adj.","风景优美的","What a scenic route!","多美的风景路线！"),
 ("explore","v.","探索","Let's explore the city.","我们去探索这座城市吧。"),
 ("navigate","v.","导航；找到路","Navigate through the crowd.","穿过人群找路。"),
 ("customs","n.","海关","Pass through customs.","过海关。"),
 ("visa","n.","签证","Apply for a visa.","申请签证。"),
 ("currency","n.","货币","Exchange currency at the airport.","在机场换货币。"),
 ("souvenir","n.","纪念品","Buy a souvenir for me.","给我买个纪念品。"),
 ("cuisine","n.","菜系；烹饪","I love Chinese cuisine.","我喜欢中国菜。"),
 ("ingredient","n.","食材","Fresh ingredients matter.","新鲜食材很重要。"),
 ("appetite","n.","胃口","I've lost my appetite.","我没胃口。"),
 ("portion","n.","份量","The portion is generous.","份量很大。"),
 ("beverage","n.","饮料","Choose a beverage.","选一种饮料。"),
 ("allergic","adj.","过敏的","I'm allergic to peanuts.","我对花生过敏。"),
 ("vegetarian","n./adj.","素食者；素食的","Are you vegetarian?","你吃素吗？"),
 ("recipe","n.","食谱","Share the recipe with me.","把食谱分享给我。"),
 ("reservation","n.","预订（位）","Make a reservation.","预订位子。"),
 ("gratuity","n.","小费","Gratuity is included.","小费已包含在内。"),
 ("mortgage","n.","房贷","Pay off the mortgage.","还清房贷。"),
 ("rental","n.","租金；租赁","The rental market is crazy.","租房市场太疯狂了。"),
 ("renovate","v.","翻新","Renovate the kitchen.","翻新厨房。"),
 ("furnished","adj.","带家具的","It's fully furnished.","是全配的。"),
 ("utilities","n.","水电燃气费","Utilities are extra.","水电费另算。"),
 ("neighborhood","n.","社区；街区","Nice neighborhood.","社区环境不错。"),
 ("commute","n./v.","通勤","My commute takes an hour.","我通勤要一小时。"),
 ("landlord","n.","房东","Talk to the landlord.","跟房东谈谈。"),
 ("deposit","n.","押金","Pay the deposit first.","先付押金。"),
 ("lease","n.","租约","Sign the lease.","签租约。"),
 ("device","n.","设备","Connect the device.","连接设备。"),
 ("application","n.","应用","Download the application.","下载应用。"),
 ("password","n.","密码","Reset your password.","重置密码。"),
 ("browse","v.","浏览","Browse the website.","浏览网站。"),
 ("download","v.","下载","Download the file.","下载文件。"),
 ("upload","v.","上传","Upload the photo.","上传照片。"),
 ("wireless","adj.","无线的","Wireless connection is slow.","无线连接很慢。"),
 ("software","n.","软件","Update the software.","更新软件。"),
 ("platform","n.","平台","Which platform do you use?","你用哪个平台？"),
 ("notification","n.","通知","Turn off notifications.","关掉通知。"),
 ("curriculum","n.","课程体系","The curriculum is comprehensive.","课程体系很全面。"),
 ("assignment","n.","作业","Finish the assignment.","完成作业。"),
 ("tuition","n.","学费","Tuition is expensive.","学费很贵。"),
 ("scholarship","n.","奖学金","Apply for a scholarship.","申请奖学金。"),
 ("certificate","n.","证书","Get a certificate.","拿个证书。"),
 ("comprehend","v.","理解","Do you comprehend?","你理解了吗？"),
 ("memorize","v.","记住","Memorize the vocabulary.","背下这些词汇。"),
 ("pronunciation","n.","发音","Work on pronunciation.","练一下发音。"),
 ("fluency","n.","流利度","Improve your fluency.","提高流利度。"),
 ("comprehension","n.","理解力","Reading comprehension is key.","阅读理解是关键。"),
 ("streaming","n.","流媒体","Streaming is popular now.","流媒体现在很流行。"),
 ("subscribe","v.","订阅","Subscribe to her channel.","订阅她的频道。"),
 ("episode","n.","一集","Watch the latest episode.","看最新一集。"),
 ("genre","n.","类型；流派","What genre do you like?","你喜欢什么类型？"),
 ("plot","n.","情节","The plot is predictable.","情节太可预测了。"),
 ("character","n.","角色","The character development is great.","角色塑造得很棒。"),
 ("review","n./v.","评论；评价","Read the reviews first.","先看看评论。"),
 ("audience","n.","观众","The audience loved it.","观众很喜欢。"),
 ("broadcast","v./n.","广播；播出","It was broadcast live.","它是直播播出的。"),
 ("trending","adj.","热门的","This topic is trending.","这个话题正在上热搜。"),
 ("sustainable","adj.","可持续的","Live sustainably.","可持续地生活。"),
 ("pollution","n.","污染","Air pollution is serious.","空气污染很严重。"),
 ("recycle","v.","回收利用","Recycle plastic bottles.","回收塑料瓶。"),
 ("carbon","n.","碳","Reduce carbon footprint.","减少碳排放。"),
 ("equality","n.","平等","Fight for equality.","为平等而战。"),
 ("discrimination","n.","歧视","Face discrimination.","面临歧视。"),
 ("diversity","n.","多样性","Value diversity.","重视多样性。"),
 ("community","n.","社区","Support the community.","支持社区发展。"),
 ("volunteer","n./v.","志愿者；做义工","I volunteer on weekends.","我周末做义工。"),
 ("donate","v.","捐赠","Donate to charity.","捐给慈善机构。"),
 ("come up with","phr.","想出","Come up with an idea.","想出一个主意。"),
 ("look forward to","phr.","期待","I look forward to seeing you.","我很期待见到你。"),
 ("get along with","phr.","和…相处","I get along with my roommate.","我和室友相处得很好。"),
 ("run out of","phr.","用完","We ran out of time.","我们时间不够了。"),
 ("put up with","phr.","忍受","I can't put up with this.","我再也无法忍受了。"),
 ("bring up","phr.","提出；抚养","Bring up the topic.","提一下这个话题。"),
 ("turn out","phr.","结果是","It turned out well.","结果还不错。"),
 ("give up","phr.","放弃","Don't give up on yourself.","别放弃自己。"),
 ("carry on","phr.","继续","Carry on with your work.","继续你的工作。"),
 ("figure out","phr.","弄明白","Figure out the solution.","想出解决方案。"),
 ("adequate","adj.","足够的；合格的","Is this adequate?","这够了吗？"),
 ("significant","adj.","重要的；显著的","A significant change.","一个重大变化。"),
 ("essential","adj.","必不可少的","Sleep is essential.","睡眠必不可少。"),
 ("efficient","adj.","高效的","Be more efficient.","更高效一点。"),
 ("appropriate","adj.","合适的","Dress appropriately.","穿着得体。"),
 ("inevitable","adj.","不可避免的","Change is inevitable.","改变是不可避免的。"),
 ("remarkable","adj.","非凡的","A remarkable achievement.","一项非凡的成就。"),
 ("sufficient","adj.","充足的","Is the evidence sufficient?","证据充分吗？"),
 ("relevant","adj.","相关的","Stay relevant.","保持相关性。"),
 ("crucial","adj.","至关重要的","Timing is crucial.","时机至关重要。"),
 ("deadline","n.","截止日期","Meet the deadline.","赶上截止日期。"),
 ("feedback","n.","反馈","Give me feedback.","给我点反馈。"),
 ("colleague","n.","同事","Ask your colleague.","问问同事。"),
 ("meeting","n.","会议","Schedule a meeting.","安排个会议。"),
 ("presentation","n.","演示","Prepare a presentation.","准备演示文稿。"),
 ("agenda","n.","议程","Set the agenda.","定议程。"),
 ("conference","n.","会议；大会","Attend the conference.","参加会议。"),
 ("contract","n.","合同","Sign the contract.","签合同。"),
 ("salary","n.","薪水","Negotiate your salary.","谈薪水。"),
 ("benefit","n.","福利；好处","Employee benefits are good.","员工福利不错。"),
 ("attraction","n.","吸引力","There's a strong attraction.","很有吸引力。"),
 ("commitment","n.","承诺；投入","Relationship needs commitment.","关系需要投入。"),
 ("vulnerable","adj.","脆弱的；敞开心扉的","It's okay to be vulnerable.","敞开心扉没关系。"),
 ("insecure","adj.","缺乏安全感的","I feel insecure sometimes.","我有时会没有安全感。"),
 ("attachment","n.","依恋","Emotional attachment runs deep.","情感依恋很深。"),
 ("chemistry","n.","化学反应；默契","We have great chemistry.","我们之间很有默契。"),
 ("breakthrough","n.","突破","A breakthrough in our talk.","谈话有了突破。"),
 ("misunderstanding","n.","误会","Clear up the misunderstanding.","消除误会。"),
 ("reassure","v.","安慰；使安心","Reassure her everything is fine.","让她放心一切都好。"),
 ("hesitate","v.","犹豫","Don't hesitate to ask.","别犹豫，尽管问。"),
 ("comprehensive","adj.","全面的","A comprehensive report.","一份全面的报告。"),
 ("controversial","adj.","有争议的","It's a controversial topic.","这是个有争议的话题。"),
 ("straightforward","adj.","直截了当的","The solution is straightforward.","解决方案很直接。"),
 ("sophisticated","adj.","复杂的；精致的","A sophisticated system.","一个复杂的系统。"),
 ("spontaneous","adj.","自发的；即兴的","A spontaneous decision.","一个即兴的决定。"),
 ("ambiguous","adj.","模棱两可的","The answer is ambiguous.","答案模棱两可。"),
 ("coincidence","n.","巧合","What a coincidence!","太巧了！"),
 ("perception","n.","看法；感知","My perception changed.","我的看法改变了。"),
 ("integrity","n.","正直；完整","A man of integrity.","一个正直的人。"),
 ("resilience","n.","韧性","Build your resilience.","建立你的韧性。"),
]

# ---------------- 2. 批量扩展词（word, pos, cn）主题分组 ----------------
# 例句由脚本按 POS 生成；中文为对应翻译
BULK = {
 "情绪与性格": [
  ("ecstatic","adj.","狂喜的"),("melancholy","adj.","忧郁的"),("compassionate","adj.","有同情心的"),
  ("temperamental","adj.","情绪化的"),("reserved","adj.","内敛的"),("outgoing","adj.","外向的"),
  ("stubborn","adj.","固执的"),("open-minded","adj.","开明的"),("considerate","adj.","体贴的"),
  ("arrogant","adj.","傲慢的"),("humble","adj.","谦逊的"),("impulsive","adj.","冲动的"),
  ("moody","adj.","情绪多变的"),("sentimental","adj.","多愁善感的"),("thrilled","adj.","极度兴奋的"),
  ("furious","adj.","暴怒的"),("grateful","adj.","感激的"),("lonely","adj.","孤独的"),
  ("optimistic","adj.","乐观的"),("pessimistic","adj.","悲观的"),("realistic","adj.","现实的"),
  ("selfish","adj.","自私的"),("generous","adj.","慷慨的"),("courageous","adj.","勇敢的"),
  ("timid","adj.","胆怯的"),("bold","adj.","大胆的"),("patient","adj.","耐心的"),
  ("impatient","adj.","不耐烦的"),("tolerant","adj.","宽容的"),("witty","adj.","机智幽默的"),
  ("sensitive","adj.","敏感的"),("cheerful","adj.","开朗的"),("gloomy","adj.","阴郁的"),
  ("sensible","adj.","明智的"),("foolish","adj.","愚蠢的"),("prudent","adj.","谨慎的"),
  ("reckless","adj.","鲁莽的"),("modest","adj.","谦虚的；适度的"),("vain","adj.","虚荣的"),
  ("ego","n.","自我；自尊心"),("intuition","n.","直觉"),("instinct","n.","本能"),
  ("conscience","n.","良心"),("subconscious","adj.","潜意识的"),("temper","n.","脾气"),
  ("mood","n.","心情"),("personality","n.","个性"),("character","n.","品格"),
  ("trauma","n.","创伤"),("grudge","n.","怨恨"),("bias","n.","偏见"),
  ("prejudice","n.","偏见；成见"),("stereotype","n.","刻板印象"),("empathy","n.","共情"),
  ("sympathy","n.","同情"),("affection","n.","喜爱"),("passion","n.","热情；激情"),
 ],
 "社交与沟通": [
  ("greet","v.","问候"),("introduce","v.","介绍"),("compliment","v.","称赞"),
  ("apologize","v.","道歉"),("forgive","v.","原谅"),("comfort","v.","安慰"),
  ("encourage","v.","鼓励"),("criticize","v.","批评"),("complain","v.","抱怨"),
  ("gossip","v.","八卦"),("interrupt","v.","打断"),("listen","v.","倾听"),
  ("confide","v.","倾诉"),("flirt","v.","调情"),("reject","v.","拒绝"),
  ("accept","v.","接受"),("invite","v.","邀请"),("decline","v.","婉拒"),
  ("negotiate","v.","协商"),("mediate","v.","调解"),("persuade","v.","劝说"),
  ("convince","v.","使信服"),("assure","v.","向…保证"),("promise","v.","承诺"),
  ("betray","v.","背叛"),("trust","v.","信任"),("doubt","v.","怀疑"),
  ("gossip","n.","闲话"),("rumor","n.","谣言"),("secret","n.","秘密"),
  ("acquaintance","n.","熟人"),("stranger","n.","陌生人"),("companion","n.","同伴"),
  ("roommate","n.","室友"),("classmate","n.","同学"),("neighbor","n.","邻居"),
  ("small talk","n.","闲聊"),("gesture","n.","手势；姿态"),("tone","n.","语气"),
  ("humor","n.","幽默"),("irony","n.","讽刺"),("sarcasm","n.","挖苦"),
  ("politeness","n.","礼貌"),("manners","n.","礼貌；举止"),("etiquette","n.","礼仪"),
  ("boundary","n.","边界；底线"),("distance","n.","距离；疏远"),("closeness","n.","亲密"),
  ("bonding","n.","增进感情"),("icebreaker","n.","破冰话题"),("small_talk","n.","寒暄"),
 ],
 "工作与职场2": [
  ("deadline","n.","截止日期"),("overtime","n.","加班"),("freelance","adj.","自由职业的"),
  ("intern","n.","实习生"),("mentor","n.","导师"),("apprentice","n.","学徒"),
  ("colleague","n.","同事"),("superior","n.","上级"),("subordinate","n.","下属"),
  ("resume","n.","简历"),("portfolio","n.","作品集"),("interview","n.","面试"),
  ("qualification","n.","资格"),("expertise","n.","专长"),("proficiency","n.","熟练"),
  ("promotion","n.","晋升"),("raise","n.","加薪"),("bonus","n.","奖金"),
  ("layoff","n.","裁员"),("retire","v.","退休"),("quit","v.","辞职"),
  ("hire","v.","雇佣"),("fire","v.","解雇"),("outsource","v.","外包"),
  ("brainstorm","v.","头脑风暴"),("delegate","v.","委派"),("streamline","v.","精简"),
  ("optimize","v.","优化"),("automate","v.","自动化"),("scale","v.","扩大规模"),
  ("revenue","n.","收入"),("overhead","n.","运营开支"),("cashflow","n.","现金流"),
  ("stakeholder","n.","利益相关者"),("client","n.","客户"),("vendor","n.","供应商"),
  ("networking","n.","人脉拓展"),("pitch","n.","推销；提案"),("proposal","n.","提案"),
  ("milestone","n.","里程碑"),("benchmark","n.","基准"),("KPI","n.","关键绩效指标"),
  ("agile","adj.","敏捷的"),("redundant","adj.","冗余的；被裁的"),("tenure","n.","任期；终身聘用"),
  ("hierarchy","n.","等级制度"),("bureaucracy","n.","官僚作风"),("startup","n.","初创公司"),
  ("entrepreneur","n.","企业家"),("corporate","adj.","公司的"),("remote_work","n.","远程办公"),
 ],
 "生活与日常2": [
  ("grocery","n.","杂货"),("laundry","n.","洗衣"),("chore","n.","家务"),
  ("errand","n.","差事"),("routine","n.","例行习惯"),("habit","n.","习惯"),
  ("lifestyle","n.","生活方式"),("balanced","adj.","平衡的"),("moderate","adj.","适度的"),
  ("occasional","adj.","偶尔的"),("frequent","adj.","频繁的"),("rare","adj.","罕见的"),
  ("household","n.","家庭；家务"),("appliance","n.","家电"),("furniture","n.","家具"),
  ("decoration","n.","装饰"),("messy","adj.","凌乱的"),("tidy","adj.","整洁的"),
  ("spacious","adj.","宽敞的"),("cramped","adj.","狭窄的"),("cozy","adj.","舒适的"),
  ("leak","v.","漏水"),("repair","v.","修理"),("maintain","v.","维护"),
  ("breakdown","n.","故障"),("power outage","n.","停电"),("plumber","n.","水管工"),
  ("appointment","n.","预约"),("reminder","n.","提醒"),("schedule","n.","日程"),
  ("commute","n.","通勤"),("traffic","n.","交通"),("jam","n.","拥堵"),
  ("parking","n.","停车"),("pedestrian","n.","行人"),("crosswalk","n.","斑马线"),
  ("sidewalk","n.","人行道"),("intersection","n.","十字路口"),("roundabout","n.","环岛"),
  ("subway","n.","地铁"),("bus stop","n.","公交站"),("railway","n.","铁路"),
  ("domestic","adj.","国内的；家务的"),("abroad","adv.","在国外"),("luggage","n.","行李"),
  ("suitcase","n.","手提箱"),("backpack","n.","背包"),("check-in","n.","办理登机/入住"),
 ],
 "健康与运动2": [
  ("workout","n.","训练"),("cardio","n.","心肺运动"),("strength","n.","力量"),
  ("flexibility","n.","柔韧性"),("endurance","n.","耐力"),("posture","n.","体态"),
  ("warm-up","n.","热身"),("cool-down","n.","放松"),("rep","n.","一次反复"),
  ("set","n.","组"),("muscle","n.","肌肉"),("joint","n.","关节"),
  ("injury","n.","受伤"),("sprain","n.","扭伤"),("fracture","n.","骨折"),
  ("rehab","n.","康复"),("hydrate","v.","补水"),("stretch","v.","拉伸"),
  ("jog","v.","慢跑"),("sprint","v.","冲刺"),("yoga","n.","瑜伽"),
  ("pilates","n.","普拉提"),("meditate","v.","冥想"),("breathe","v.","呼吸"),
  ("immune","adj.","免疫的"),("vitamin","n.","维生素"),("protein","n.","蛋白质"),
  ("calorie","n.","卡路里"),("carb","n.","碳水"),("fat","n.","脂肪"),
  ("vegan","n./adj.","纯素者；纯素的"),("gluten-free","adj.","无麸质的"),("organic","adj.","有机的"),
  ("addictive","adj.","上瘾的"),("withdraw","v.","戒断；退出"),("relapse","n.","复发"),
  ("checkup","n.","体检"),("prescription","n.","处方"),("diagnosis","n.","诊断"),
  ("symptom","n.","症状"),("preventive","adj.","预防性的"),("sedentary","adj.","久坐的"),
  ("posture","n.","姿势"),("burnout","n.","倦怠"),("wellness","n.","健康；养生"),
 ],
 "金钱与消费2": [
  ("savings","n.","储蓄"),("debt","n.","债务"),("loan","n.","贷款"),
  ("credit","n.","信用"),("interest","n.","利息"),("inflation","n.","通货膨胀"),
  ("premium","n.","溢价；保费"),("subscription","n.","订阅费"),("refund","n.","退款"),
  ("bargain","n.","便宜货；讨价还价"),("overpriced","adj.","定价过高的"),("worthwhile","adj.","值得的"),
  ("frugal","adj.","节俭的"),("extravagant","adj.","奢侈浪费的"),("stingy","adj.","吝啬的"),
  ("broke","adj.","破产的；没钱的"),("wealthy","adj.","富有的"),("bankrupt","adj.","破产的"),
  ("donation","n.","捐赠"),("charity","n.","慈善"),("tax","n.","税"),
  ("pension","n.","养老金"),("allowance","n.","津贴"),("salary","n.","月薪"),
  ("wage","n.","时薪；工资"),("income","n.","收入"),("expense","n.","支出"),
  ("budget","n.","预算"),("overdraft","n.","透支"),("mortgage","n.","按揭"),
  ("investment","n.","投资"),("portfolio","n.","投资组合"),("dividend","n.","股息"),
  ("crypto","n.","加密货币"),("stock","n.","股票"),("bond","n.","债券"),
  ("insurance","n.","保险"),("claim","n.","索赔"),("coverage","n.","承保范围"),
  ("fraud","n.","欺诈"),("scam","n.","骗局"),("counterfeit","adj.","伪造的"),
  ("thrifty","adj.","节约的"),("lavish","adj.","奢华的"),("modest","adj.","适中的"),
 ],
 "学习与方法2": [
  ("diligent","adj.","勤奋的"),("studious","adj.","好学的"),("curious","adj.","好奇的"),
  ("knowledgeable","adj.","知识渊博的"),("ignorant","adj.","无知的"),("illiterate","adj.","不识字的"),
  ("skim","v.","略读"),("scan","v.","扫读"),("summarize","v.","总结"),
  ("paraphrase","v.","转述"),("quote","v.","引用"),("cite","v.","引用；引证"),
  ("annotate","v.","注释"),("outline","v.","列提纲"),("draft","v.","起草"),
  ("revise","v.","修订"),("proofread","v.","校对"),("memorize","v.","记忆"),
  ("recall","v.","回忆"),("retain","v.","保留"),("absorb","v.","吸收"),
  ("grasp","v.","掌握"),("master","v.","精通"),("practice","v.","练习"),
  ("fluent","adj.","流利的"),("bilingual","adj.","双语的"),("multilingual","adj.","多语的"),
  ("academy","n.","学院"),("seminar","n.","研讨班"),("tutorial","n.","辅导"),
  ("lecture","n.","讲座"),("syllabus","n.","教学大纲"),("enroll","v.","报名"),
  ("graduate","v.","毕业"),("dropout","n.","辍学者"),("truant","n.","逃学者"),
  ("discipline","n.","学科；自律"),("major","n.","专业"),("minor","n.","辅修"),
  ("thesis","n.","论文"),("research","n.","研究"),("fieldwork","n.","实地调研"),
  ("peer","n.","同辈；同行"),("mentor","n.","导师"),("tutor","n.","家教"),
 ],
 "科学与技术2": [
  ("algorithm","n.","算法"),("artificial","adj.","人工的"),("intelligence","n.","智能"),
  ("machine learning","n.","机器学习"),("neural","adj.","神经的"),("data","n.","数据"),
  ("database","n.","数据库"),("cloud","n.","云"),("server","n.","服务器"),
  ("encrypt","v.","加密"),("decrypt","v.","解密"),("hacker","n.","黑客"),
  ("malware","n.","恶意软件"),("phishing","n.","钓鱼攻击"),("firewall","n.","防火墙"),
  ("bandwidth","n.","带宽"),("latency","n.","延迟"),("bug","n.","故障；漏洞"),
  ("patch","n.","补丁"),("update","n.","更新"),("upgrade","v.","升级"),
  ("innovation","n.","创新"),("invention","n.","发明"),("patent","n.","专利"),
  ("research","n.","科研"),("experiment","n.","实验"),("hypothesis","n.","假设"),
  ("quantum","adj.","量子的"),("genetic","adj.","基因的"),("molecular","adj.","分子的"),
  ("renewable","adj.","可再生的"),("solar","adj.","太阳能的"),("nuclear","adj.","核能的"),
  ("battery","n.","电池"),("charge","v.","充电"),("voltage","n.","电压"),
  ("sensor","n.","传感器"),("robotics","n.","机器人技术"),("automation","n.","自动化"),
  ("virtual","adj.","虚拟的"),("augmented","adj.","增强的"),("simulate","v.","模拟"),
  ("compute","v.","计算"),("process","v.","处理"),("transmit","v.","传输"),
 ],
 "社会与话题2": [
  ("democracy","n.","民主"),("election","n.","选举"),("policy","n.","政策"),
  ("reform","n.","改革"),("welfare","n.","福利"),("poverty","n.","贫困"),
  ("inequality","n.","不平等"),("migrant","n.","移民"),("refugee","n.","难民"),
  ("citizen","n.","公民"),("rights","n.","权利"),("freedom","n.","自由"),
  ("censorship","n.","审查"),("propaganda","n.","宣传"),("corruption","n.","腐败"),
  ("transparent","adj.","透明的"),("accountable","adj.","问责的"),("justice","n.","正义"),
  ("crime","n.","犯罪"),("punishment","n.","惩罚"),("rehabilitation","n.","改造；康复"),
  ("activism","n.","行动主义"),("protest","n.","抗议"),("petition","n.","请愿"),
  ("boycott","v.","抵制"),("sanction","n.","制裁"),("diplomacy","n.","外交"),
  ("treaty","n.","条约"),("alliance","n.","联盟"),("conflict","n.","冲突"),
  ("peacekeeping","n.","维和"),("humanitarian","adj.","人道主义的"),("sustainable","adj.","可持续的"),
  ("urban","adj.","城市的"),("rural","adj.","农村的"),("suburb","n.","郊区"),
  ("infrastructure","n.","基础设施"),("sanitation","n.","卫生设施"),("recycling","n.","回收"),
  ("emission","n.","排放"),("conservation","n.","保护"),("wildlife","n.","野生动物"),
 ],
 "描述与评价2": [
  ("vivid","adj.","生动的"),("subtle","adj.","微妙的"),("obvious","adj.","明显的"),
  ("vague","adj.","模糊的"),("precise","adj.","精确的"),("accurate","adj.","准确的"),
  ("rough","adj.","粗略的"),("detailed","adj.","详细的"),("concise","adj.","简洁的"),
  ("lengthy","adj.","冗长的"),("brief","adj.","简短的"),("thorough","adj.","彻底的"),
  ("shallow","adj.","肤浅的"),("profound","adj.","深刻的"),("trivial","adj.","微不足道的"),
  ("crucial","adj.","关键的"),("minor","adj.","次要的"),("major","adj.","主要的"),
  ("superficial","adj.","表面的"),("genuine","adj.","真正的"),("fake","adj.","假的"),
  ("authentic","adj.","正宗的；真实的"),("artificial","adj.","人造的"),("natural","adj.","自然的"),
  ("elegant","adj.","优雅的"),("clumsy","adj.","笨拙的"),("graceful","adj.","优雅的"),
  ("awkward","adj.","尴尬的"),("smooth","adj.","顺利的"),("tricky","adj.","棘手的"),
  ("challenging","adj.","有挑战的"),("effortless","adj.","轻松的"),("tedious","adj.","乏味的"),
  ("fascinating","adj.","迷人的"),("boring","adj.","无聊的"),("amusing","adj.","有趣的"),
  ("touching","adj.","感人的"),("hilarious","adj.","极好笑的"),("depressing","adj.","令人沮丧的"),
 ],
}

# ---------------- 例句模板（POS 感知） ----------------
def make_ex(w, pos, cn):
    p = pos.lower()
    if 'phr' in p:
        # 短语用通用自然句
        return f"Try to {w} in daily conversation.", f"试着在日常对话里用「{cn}」。"
    if 'adv' in p:
        return f"She explained it {w}.", f"她{wcn(cn)}解释了一遍。"
    if 'v' in p:
        return f"I try to {w} regularly.", f"我试着经常{wcn(cn)}。"
    if 'adj' in p:
        return f"That sounds {w}.", f"那听起来很{cn}。"
    # 默认名词
    return f"This {w} really matters.", f"这个{cn}真的很关键。"

def wcn(cn):
    # 让动词中文更自然一点（去掉末尾“的”）
    return cn.rstrip('的')

# ---------------- 组装（含音标 ph） ----------------
def add_ph(w):
    try:
        p = ipa(w)
        return '/' + p + '/' if p else ''
    except Exception:
        return ''

def esc(s):
    return s.replace('\\','\\\\').replace('"','\\"')

entries = []
seen = set()

# 核心精校
for (w,pos,cn,ex,zh) in CORE:
    if w.lower() in seen: continue
    seen.add(w.lower())
    entries.append((w,pos,add_ph(w),cn,ex,zh))

# 批量主题
for theme, lst in BULK.items():
    for (w,pos,cn) in lst:
        if w.lower() in seen: continue
        seen.add(w.lower())
        ex,zh = make_ex(w,pos,cn)
        entries.append((w,pos,add_ph(w),cn,ex,zh))

# 大规模扩展词库（目标 ~3000）
for src in (wordbank1.EXTRA, wordbank2.EXTRA, wordbank3.EXTRA, wordbank4.EXTRA, wordbank5.EXTRA):
    for (w,pos,cn) in src:
        if w.lower() in seen: continue
        seen.add(w.lower())
        ex,zh = make_ex(w,pos,cn)
        entries.append((w,pos,add_ph(w),cn,ex,zh))

# 打乱顺序（避免同主题扎堆），但保持可复现
random.seed(20260730)
random.shuffle(entries)

# 输出 JS 数组（含音标 ph）
lines = []
for (w,pos,ph,cn,ex,zh) in entries:
    lines.append(f' {{w:"{esc(w)}",pos:"{esc(pos)}",ph:"{esc(ph)}",cn:"{esc(cn)}",ex:"{esc(ex)}",zh:"{esc(zh)}"}}')
body = ",\n ".join(lines)
out = "const B1_WORDS=[\n " + body + "\n];"
with open("words_out.js","w",encoding="utf-8") as f:
    f.write(out)
print("TOTAL:", len(entries))
print("UNIQUE:", len(seen))
