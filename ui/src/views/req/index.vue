<template lang="pug">
  .login-container
    .app-container
      .title-container
        h3.title 注册申请

      el-steps(style={ width: '520px', margin: '0 auto' }, :active="step", finish-status="success")
        el-step(title="阅读规则")
        el-step(title="入服测试")
        el-step(title="提交申请")
        el-step(title="完成申请")

      div.paddintop(v-if="step === 0", align="center")
        div
          span 你好，欢迎来到XJcraft！
          span 请下载并阅读规则哟

        div(style={ 'margin-top': '32px' })
          el-button(:disabled="step0.step === 1", @click="clickStep0") {{ step0.btnName }}

      div.paddintop(v-else-if="step === 1", style={ width: '600px', margin: '0 auto', color: '#eee' })
        div(v-for="(qa, idx) in step1.qa", :key="idx", style={ 'margin-top': '8px' })
          //- 题目区
          p(v-if="qa.type !== 'input'")
           span {{ idx + 1 }}.&nbsp;
           span {{ qa.question }}
           span &nbsp;({{ qa.score }}分)
          p(v-else)
            span {{ idx + 1 }}.&nbsp;
            span.inputType(v-for="(q, idx2) in qa.question", :key="idx2")
              span(v-if="q") {{ q }}
              el-input(v-else, v-model="qa.player[(idx2 - 1) / 2]")
            span &nbsp;({{ qa.score }}分)
          //- 选项区
          //- TODO 加个 debug 显示正确答案？
          div(style={ 'margin-left': '20px' })
            div(v-if="qa.type === 'radio'")
              el-radio-group(v-model="qa.player")
                div(v-for="idx3 in qa.shuff", :key="idx3")
                  el-radio(:label="idx3", style={ color: '#eee', 'margin-top': '8px' }) {{ qa.answer[idx3] }}
            div(v-else-if="qa.type === 'checkbox'")
              el-checkbox-group(v-model="qa.player")
                div(v-for="idx3 in qa.shuff", :key="idx3")
                  el-checkbox(:label="idx3", style={ color: '#eee', 'margin-top': '8px' }) {{ qa.answer[idx3] }}
            div(v-else-if="qa.type === 'switch'")
              el-radio-group(v-model="qa.player")
                el-radio(:label="false", style={ color: '#eee', 'margin-top': '8px' }) {{ (qa.answer && qa.answer[0]) || '错误' }}
                el-radio(:label="true", style={ color: '#eee', 'margin-top': '8px' }) {{ (qa.answer && qa.answer[1]) || '正确' }}

        div(style={ 'margin-top': '50px' }, align="center")
          el-button(:disabled="step1.disabled", @click="clickStep1") {{ step1.btnName }}

      div.paddintop(v-else-if="step === 2")
        el-form.login-form(ref="reqForm", :model="reqForm", :rules="reqRules", autocomplete="off", label-position="left")
          el-form-item(prop="player_name")
            el-input(
              ref="player_name",
              v-model="reqForm.player_name",
              placeholder="玩家名",
              name="player_name",
              type="text",
              tabindex="1"
            )

          el-tooltip(v-model="capsTooltip", content="大写锁定已开启", placement="right", manual)
            el-form-item(prop="password")
              el-input(
                :key="passwordType",
                ref="password",
                v-model="reqForm.password",
                :type="passwordType",
                placeholder="密码",
                name="password",
                tabindex="2",
                autocomplete="on",
                @keyup.native="checkCapslock",
                @blur="capsTooltip = false",
                @keyup.enter.native="handleLogin"
              )
              span.show-pwd(@click="showPwd")
                svg-icon(:icon-class="passwordType === 'password' ? 'eye' : 'eye-open'")

          el-form-item(prop="qq")
            el-input(
              ref="qq",
              v-model="reqForm.qq",
              placeholder="QQ 号",
              name="qq",
              type="text",
              tabindex="3"
            )

          el-form-item(prop="type")
            el-select(
              ref="type",
              v-model="reqForm.type",
              placeholder="申请类型",
              name="type",
              tabindex="4",
              style="width: 100%"
            )
              el-option(key="", label="请选择申请类型", value="")
              el-option(key="QQLevel", label="我的 QQ 等级已达到太阳", value="QQLevel")
              el-option(key="Invite", label="老玩家邀请", value="Invite")
              el-option(key="PYJY", label="与 OP 协商", value="PYJY")

          el-form-item(v-if="reqForm.type === 'Invite'", prop="old_player_name")
            el-input(
              ref="old_player_name",
              v-model="reqForm.old_player_name",
              placeholder="邀请人(玩家名)",
              name="old_player_name",
              type="text",
              tabindex="3"
            )

          el-form-item(v-if="reqForm.type === 'PYJY'", prop="op_name")
            el-input(
              ref="op_name",
              v-model="reqForm.op_name",
              placeholder="OP(玩家名)",
              name="op_name",
              type="text",
              tabindex="3"
            )

          el-button(:loading="loading", type="primary", style="width: 100%; margin-bottom: 30px;", @click.native.prevent="handleReq") 提交申请

      div.paddintop(v-else-if="step === 3", align="center")
        div 申请成功，请耐心等待 OP 处理
        div(style={ 'margin-top': '32px' })
          el-button(@click="clickStep3") 查询处理进度
    footer(align="center")
      a(href="http://www.beian.miit.gov.cn/", target="_blank") 陕ICP备19017184号
</template>

<script>
import { validUsername } from '@/utils/validate'
import { req } from '@/api/req'
import { notifySuccess, notifyWarn } from '../../utils/notify'

export default {
  name: 'Req',
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!validUsername(value)) {
        callback(new Error('请输入有效的玩家名(大小写字母、数字和下划线，3 ~ 16 位)'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码不能少于 6 位'))
      } else if (value.length > 50) {
        callback(new Error('密码不能多于 50 位'))
      } else {
        callback()
      }
    }
    const validateQQ = (rule, value, callback) => {
      if (/^\d{5,11}$/.test(value)) {
        callback()
      } else {
        callback(new Error('请输入有效的 QQ 号'))
      }
    }
    const validateType = (rule, value, callback) => {
      if (value !== '') {
        callback()
      } else {
        callback(new Error('请选择申请类型'))
      }
    }
    return {
      step: this.$route.query.skip === 'xj' ? Number(this.$route.query.step) : 0,
      step0: {
        btnName: '点击下载规则',
        step: 0,
        waitTime: 300
      },
      step1: {
        // 题目
        qa: [
        //  { // 单选题
        //    type: 'radio',
        //    question: '单选题 - 合成一个工作台需要几个木板？',
        //    answer: [
        //      '1',
        //      '2',
        //      '3',
        //      '4'
        //    ],
        //    score: 5,
        //    correct: 3
        //  },
        //  { // 多选题
        //    type: 'checkbox',
        //    question: '多选题 - 哪些是合成信标需要的材料？',
        //    answer: [
        //      '沙子',
        //      '黑曜石',
        //      '水桶',
        //      '玻璃'
        //    ],
        //    score: 5,
        //    correct: [1, 3]
        //  },
        //  { // 判断题
        //    type: 'switch',
        //    question: '判断题 - 在服务器里可以随便熊',
        //    score: 5,
        //    correct: false
        //  },
        //  { // 判断题，自定义错误和正确的内容，第一个对应 false，第二个对应 true
        //    type: 'switch',
        //    question: '判断题 - 服务器里可以熊么？',
        //    answer: ['不可以', '可以'],
        //    score: 5,
        //    correct: false
        //  },
        //  { // 填空题
        //    type: 'input',
        //    // 注意，最后一个空就在结尾时，即使后面什么都没有，也要写点什么，比如句号，甚至一个空字符串: ''
        //    // 同理，第一个空在开头时，前面也要写点什么，哪怕是个空字符串
        //    question: ['填空题 - 合成一个信标需要', '个黑曜石、', '个玻璃、以及一个', '。'],
        //    score: 5,
        //    correct: [
        //      // 每个数组是一个空的答案，填里面任意一个都算对，判题的时候会自动去掉两边的空格，因此答案里也不要带两边空格
        //      // 对于字母，会忽略大小写
        //      ['3', '三'],
        //      ['5', '五'],
        //      ['下界之星', '星星', 'Nether Star', 'NetherStar', 'Star']
        //    ]
        //  },
          // 以上为示例，问题请参照上面的往后加

          { // 单选题
            type: 'radio',
            question: 'Minecraft是一个（ ）游戏',
            answer: [
              ' Role playing Game',
              ' Sandbox Game',
              ' Shooting Game',
              ' Love Game'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题
            type: 'radio',
            question: 'Minecraft 游戏模式有（ ）种',
            answer: [
              ' 3',
              ' 4',
              ' 5',
              ' 6'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题
            type: 'checkbox',
            question: '进入生存模式的第一件事是（ ）（多选）',
            answer: [
              ' 看风景',
              ' 去玩水',
              ' 撸木头',
              ' 跳山谷'
            ],
            score: 2,
            correct: [0, 1, 2, 3]
          },
          { // 单选题
            type: 'radio',
            question: '有时可以增加稀有掉落的附魔是？',
            answer: [
              ' 时运',
              ' 抢夺',
              ' 海之眷顾',
              ' 效率'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题
            type: 'radio',
            question: '去地狱需要什么？',
            answer: [
              ' 自杀',
              ' 黑曜石',
              ' 钻石块',
              ' 地狱岩'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题
            type: 'radio',
            question: '云的高度是？',
            answer: [
              ' 128-156',
              ' 108-112',
              ' 100-104',
              ' 126-140'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题
            type: 'radio',
            question: '下面哪个物品不能作为燃料？',
            answer: [
              ' 木板',
              ' 橡木',
              ' 烈焰棒',
              ' 海带'
            ],
            score: 2,
            correct: 3
          },
          { // 单选题
            type: 'radio',
            question: '玩家有几颗心？',
            answer: [
              ' 5',
              ' 10',
              ' 15',
              ' 20'
            ],
            score: 2,
            correct: 1
          },
          { // 多选题
            type: 'checkbox',
            question: 'Minecraft里交通工具有（ ）（多选）',
            answer: [
              ' 猪',
              ' 船',
              ' 马',
              ' 羊'
            ],
            score: 2,
            correct: [0, 1, 2]
          },
          { // 单选题
            type: 'radio',
            question: '染料有多少种？',
            answer: [
              ' 13',
              ' 14',
              ' 15',
              ' 16'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题
            type: 'radio',
            question: '充能苦力怕需要对苦力怕做什么？',
            answer: [
              ' 红石充能',
              ' 被雷劈中',
              ' 用带有火焰附加的钻石剑劈',
              ' 诱导海底守卫攻击'

            ],
            score: 2,
            correct: 1
          },
          { // 单选题
            type: 'radio',
            question: '恶魂的碰撞箱大小是？',
            answer: [
              ' 4*4*4',
              ' 5*5*5',
              ' 4*4*5',
              ' 5*5*4'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题
            type: 'radio',
            question: '蜘蛛在亮度低于多少时会主动攻击玩家？',
            answer: [
              ' 3',
              ' 7',
              ' 11',
              ' 一直会攻击，与亮度无关'
            ],
            score: 2,
            correct: 2
          },
          { // 多选题
            type: 'checkbox',
            question: '僵尸的掉落物有（ ）（多选）',
            answer: [
              ' 腐肉',
              ' 铁',
              ' 骨头',
              ' 经验球'
            ],
            score: 2,
            correct: [0, 1, 3]
          },
          { // 单选题
            type: 'radio',
            question: '做一套服装（头盔，盔甲，裤子和鞋）需要多少单位物品？',
            answer: [
              ' 23',
              ' 24',
              ' 25',
              ' 26'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题
            type: 'radio',
            question: '粘土块在什么地方挖掘？',
            answer: [
              ' 沼泽区',
              ' 深海区',
              ' 浅水区',
              ' 沙漠区'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题
            type: 'radio',
            question: '下列什么物品可以用生存模式得到？',
            answer: [
              ' 苦力怕头',
              ' 基岩',
              ' 耕地',
              ' 命令方块'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题
            type: 'radio',
            question: '没有使用实体材质的技术性方块是？',
            answer: [
              ' 下界传送门方块',
              ' 末地传送门方块',
              ' 发光的黑曜石',
              ' 游戏更新方块'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题
            type: 'radio',
            question: '以下选项哪一个是中立性生物？',
            answer: [
              ' 海豚',
              ' 僵尸',
              ' 村民',
              ' 猫咪'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题
            type: 'radio',
            question: '重生末影龙会顺带重生？',
            answer: [
              ' 末影沙',
              ' 末影床',
              ' 末影水晶',
              ' 末影人'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题
            type: 'radio',
            question: '从哪里修改群名片？',
            answer: [
              ' QQ昵称',
              ' 群设置',
              ' 个人资料',
              ' 查找'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题
            type: 'radio',
            question: '群里的文件在哪里？',
            answer: [
              ' 群公告',
              ' 群相册',
              ' 群文件',
              ' 群应用'
            ],
            score: 2,
            correct: 2
          },
          { // 多选题
            type: 'radio',
            question: 'QQ群普通成员不可以看到什么？',
            answer: [
              ' 进群时间',
              ' 发言数量',
              ' 成员分布',
              ' 性别'
            ],
            score: 2,
            correct: 1
          },
          { // 多选题
            type: 'checkbox',
            question: 'Pdf格式的文件用什么打开？（多选）',
            answer: [
              ' JisuPdf',
              ' Abode Reader',
              ' 记事本',
              ' Microsoft Office Word'
            ],
            score: 2,
            correct: [0, 1, 3]
          },
          { // 单选题
            type: 'checkbox',
            question: 'Pdf的文件可以修改什么？（多选）',
            answer: [
              ' 文件名',
              ' 文件内容',
              ' 文件引用',
              ' 文件格式'
            ],
            score: 2,
            correct: [0, 1, 2, 3]
          },
          { // 单选题1
            type: 'radio',
            question: '有新人加入问服务器IP，我应该怎么办',
            answer: [
              ' 让他看群公告',
              ' 在群里发布IP',
              ' 私聊告诉他IP',
              ' 让他爆照来换IP'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题2
            type: 'radio',
            question: '以下行为哪种不可取',
            answer: [
              ' 劝新玩家过不去时自杀重新开始',
              ' 拿黑曜石去围住白名玩家的床',
              ' 利用迷宫特性过迷宫',
              ' 直接给新人过考核的提示'
            ],
            score: 2,
            correct: 3
          },
          { // 单选题3
            type: 'radio',
            question: '过生存考核需要什么',
            answer: [
              ' 铁套',
              ' 30颗钻石',
              ' 钻石盔甲',
              ' 钻石盔甲+钻石镐+钻石剑'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题4
            type: 'radio',
            question: '过了考核之后，以下那种行为是允许的',
            answer: [
              ' 改造新手宿舍',
              ' 去粘土山小镇挖粘土，去蘑菇岛小镇挖菌丝',
              ' 去公共小黑塔拿珍珠',
              ' 去蘑菇岛小镇建刷珊瑚农场'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题5
            type: 'radio',
            question: '以下哪种行为会被OP提醒改造',
            answer: [
              ' 带开关的高频红石电路',
              ' 单一动物超过20只',
              ' 高空流水',
              ' 往小镇房子的箱子里放物品'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题6
            type: 'radio',
            question: '当一个玩家在门前写禁止参观，而你执意进去参观之后，你会受到什么惩罚',
            answer: [
              ' 被ban',
              ' 被关监狱',
              ' 在群里公示，并被要求道歉',
              ' 以上均有可能'
            ],
            score: 2,
            correct: 3
          },
          { // 单选题7
            type: 'checkbox',
            question: '去参观别人机器时，手上突然多了一颗红石，这时候你不该怎么做（多选）',
            answer: [
              ' 把红石放在玩家基地的箱子里',
              ' 迅速在群里@该基地玩家，@不出来私聊，私聊不到找OP',
              ' 带走红石，赔他一颗钻石。',
              ' 我是红石大佬，我可以修好……'
            ],
            score: 2,
            correct: [0, 2]
          },
          { // 单选题8
            type: 'radio',
            question: '遇见有名字的僵尸，一下哪种行为是错误的',
            answer: [
              ' 服务器装了插件，这是boss级僵尸，打死就行了',
              ' 溜之大吉，不做任何动作',
              ' 把僵尸围起来',
              ' 在服里喊人来围观'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题9
            type: 'checkbox',
            question: '在其他玩家没明说的情况下，我可以做什么（多选）',
            answer: [
              ' 剪玩家基地羊毛',
              ' 撸玩家基地的土豆，并种上',
              ' 挤玩家基地的奶牛',
              ' 使用别人家的村民交易'
            ],
            score: 2,
            correct: [0, 1, 2]
          },
          { // 单选题10
            type: 'radio',
            question: '以下哪种行为不会被ban，但是会被人唾弃',
            answer: [
              ' 偷走其他玩家的物品',
              ' 用钻石剑击杀绿名玩家',
              ' 在别人床边放岩浆',
              ' 在商店反复拿取放入，制造大量CO记录。'
            ],
            score: 2,
            correct: 3
          },
          { // 单选题11
            type: 'radio',
            question: '一下那些项条件不是迁出新手宿舍的必备条件',
            answer: [
              ' 拥有建筑师执照',
              ' 拥有国债',
              ' 清空宿舍',
              ' 往政府大楼投入申请'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题12
            type: 'checkbox',
            question: '蘑菇镇的地皮价格是多少（多选）',
            answer: [
              ' 1024国债',
              ' 512国债',
              ' 768国债',
              ' 128国债'

            ],
            score: 2,
            correct: [0, 1, 2]
          },
          { // 单选题13
            type: 'radio',
            question: '服务器商店交易不需要考虑的是',
            answer: [
              ' 货币类型',
              ' 商品价格',
              ' 卖家ID',
              ' 卖家的其他要求'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题14
            type: 'radio',
            question: '以下说法正确的是',
            answer: [
              ' 挖了黑曜石柱子之后必须要打龙恢复',
              ' 挖得少可以不用打龙',
              ' 挖主岛末地石可以不用打龙',
              ' 打龙之后发现末地信标被破坏了，需要找OP来修复他'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题15
            type: 'radio',
            question: '被人恶意PVP了怎么办',
            answer: [
              ' 当然是选择原谅他咯',
              ' 向OP申述，根据他后续表现来选择ban不ban他 ',
              ' 不用废话，跟OP说一声之后抄他的家',
              ' 找人群殴他，堵着他的床杀他'
            ],
            score: 2,
            correct: 1
          },
          { // 单选题16
            type: 'radio',
            question: '以下哪种命令在服务器不能使用',
            answer: [
              ' /co i',
              ' /hat',
              ' /tpa',
              ' /xjcraft apply'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题17
            type: 'radio',
            question: '以下哪个选项不是服务器专用名词',
            answer: [
              ' 国债',
              ' 矿机',
              ' 股票',
              ' 坑'
            ],
            score: 2,
            correct: 2
          },
          { // 单选题18
            type: 'checkbox',
            question: '在小镇浏览时突然遇见了苦力怕爆炸，以下那种做法是错误的（多选）',
            answer: [
              ' 恢复原样',
              ' 又不是我挖的，不用管。',
              ' 把现场截图，并告诉附近居民此处需要点亮',
              ' 不用恢复，把周围用火把插亮就行了'
            ],
            score: 2,
            correct: [1, 3]
          },
          { // 单选题19
            type: 'radio',
            question: '以下说法正确的是',
            answer: [
              ' 生存世界不能破坏其他人的任何建筑',
              ' 坑里（创造世界）可以破坏其他人的建筑',
              ' 坑里（创造世界）可以恶意PVP，反正大家都是创造模式',
              ' 坑里没有生存世界的实体限制，可以放很多生物。'
            ],
            score: 2,
            correct: 0
          },
          { // 单选题20
            type: 'checkbox',
            question: '原版游戏中，能够点燃方块的物品有（多选）',
            answer: [
              ' 岩浆',
              ' 燃烧的箭',
              ' 火',
              ' 燃烧弹'
            ],
            score: 2,
            correct: [0, 2, 3]
          },
          { // 单选题21
            type: 'radio',
            question: '以下物品能做出床的选项是',
            answer: [
              ' 3羊毛，1橡木',
              ' 3羊毛，6木板',
              ' 12线，6木板',
              ' 12线，2橡木'
            ],
            score: 2,
            correct: 3
          },
          { // 单选题22
            type: 'radio',
            question: '以下那种物品恢复的血量最多',
            answer: [
              ' 金苹果',
              ' 治疗2药水',
              ' 生命恢复2药水',
              ' 生命恢复效果的信标'
            ],
            score: 2,
            correct: 3
          },
          { // 单选题23
            type: 'checkbox',
            question: '床 的作用有那些（多选）',
            answer: [
              ' 重置出生点',
              ' 减少掉落伤害',
              ' 驱赶苦力怕',
              ' 跳过黑夜'
            ],
            score: 2,
            correct: [0, 1, 3]
          },
          { // 单选题24
            type: 'radio',
            question: '以下哪个群系有树',
            answer: [
              ' 沙漠群系',
              ' 蘑菇岛群系',
              ' 暖洋群系',
              ' 向日葵平原群系'
            ],
            score: 2,
            correct: 3
          },
          { // 单选题25
            type: 'radio',
            question: '以下哪种村民出售命名牌',
            answer: [
              ' 盔甲商',
              ' 工具商',
              ' 图书管理员',
              ' 渔夫'
            ],
            score: 2,
            correct: 2
          }
        ],
        // 所有题目总分数(自动计算)
        totalScore: -1,
        // 最低多少分可以过
        minScore: 80,
        btnName: '答题完毕，下一步',
        disabled: false,
        wait: 120
      },
      reqForm: {
        player_name: '',
        password: '',
        qq: '',
        type: '',
        old_player_name: '',
        op_name: ''
      },
      reqRules: {
        player_name: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }],
        qq: [{ required: true, trigger: 'blur', validator: validateQQ }],
        type: [{ required: true, trigger: 'blur', validator: validateType }],
        old_player_name: [{ required: () => this.type === 'Invite', trigger: 'blur', validator: validateUsername }],
        op_name: [{ required: () => this.type === 'PYJY', trigger: 'blur', validator: validateUsername }]
      },
      passwordType: 'password',
      capsTooltip: false,
      loading: false
    }
  },
  mounted() {
    let totalScore = 0
    for (let i = this.step1.qa.length - 1; i >= 0; i--) {
      const qa = this.step1.qa[i]

      // 总分计算
      totalScore += qa.score

      // input 特殊处理
      if (qa.type === 'input') {
        for (let j = qa.question.length - 1; j >= 1; j--) {
          qa.question.splice(j, 0, void 0)
        }
      }

      // player 字段
      switch (qa.type) {
        case 'radio':
          this.$set(qa, 'player', -1)
          break
        case 'checkbox':
          this.$set(qa, 'player', [])
          break
        case 'switch':
          this.$set(qa, 'player', void 0)
          break
        case 'input':
          this.$set(qa, 'player', [])
          break
      }

      // shuff
      switch (qa.type) {
        case 'radio':
        case 'checkbox':
          this.$set(qa, 'shuff', [])
          break
      }
      if (qa.shuff) {
        const len = qa.answer.length
        for (let i = 0; i < len; i++) {
          qa.shuff.push(i)
        }
        for (let i = 0; i < len; i++) {
          const j = Math.floor(Math.random() * (len - i) + i)
          const tmp = qa.shuff[j]
          qa.shuff[j] = qa.shuff[i]
          qa.shuff[i] = tmp
        }
      }
    }
    this.totalScore = totalScore

    console.log('总分: ' + totalScore)
  },
  methods: {
    checkCapslock(e) {
      const { key } = e
      this.capsTooltip = key && key.length === 1 && (key >= 'A' && key <= 'Z')
    },
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleReq() {
      this.$refs.reqForm.validate(valid => {
        if (valid) {
          this.loading = true
          req(this.reqForm).then(response => {
            notifySuccess('申请成功')
            this.loading = false
            this.step += 1
          }).catch(() => {
            this.loading = false
          })
        } else {
          return false
        }
      })
    },
    timeout(second, fn, done) {
      let lastRemaining = -1
      const end = new Date().getTime() + (second * 1000)
      const h = setInterval(() => {
        const remaining = Math.ceil((end - new Date().getTime()) / 1000)
        if (lastRemaining !== remaining) {
          lastRemaining = remaining
          fn(remaining, () => clearInterval(h))
        }

        if (remaining <= 0) {
          clearInterval(h)
          if (done) done()
        }
      }, 100)
    },
    clickStep0() {
      if (this.step0.step === 0) {
        window.open('http://download.xjcraft.org')

        this.step0.step = 1
        this.timeout(this.step0.waitTime, remaining => {
          this.step0.btnName = '已阅读，下一步(' + remaining + ')'
        }, () => {
          this.step0.btnName = '已阅读，下一步'
          this.step0.step = 2
        })
      } else if (this.step0.step === 2) {
        this.step += 1
      }
    },
    clickStep1() {
      let score = 0
      this.step1.qa.forEach(e => {
        switch (e.type) {
          case 'radio':
            if (e.correct === e.player) score += e.score
            break
          case 'checkbox':
            if (e.correct.length === e.player.length) {
              if (!e.correct.find(a => e.player.indexOf(a) < 0)) {
                score += e.score
              }
            }

            score += e.score
            break
          case 'switch':
            if (e.correct === e.player) score += e.score
            break
          case 'input':
            let err = false
            for (let i = e.player.length - 1; i >= 0; i--) {
              const playerAnswer = e.player[i].trim()
              if (e.correct[i].indexOf(playerAnswer) < 0) {
                err = true
                break
              }
            }
            if (!err) score += e.score

            break
        }
      })

      if (score > this.step1.minScore) {
        this.step += 1
      } else {
        notifyWarn('您答错的有点多呢，再努力下试试吧~')
        this.step1.disabled = true
        this.timeout(this.step1.wait, remaining => {
          this.step1.btnName = '答题完毕，下一步(' + remaining + ')'
        }, () => {
          this.step1.btnName = '答题完毕，下一步'
          this.step1.disabled = false
        })
      }
    },
    clickStep3() {
      this.$router.push({ name: '查询申请进度', params: { player_name: this.reqForm.player_name, qq: this.reqForm.qq }})
    }
  }
}
</script>

<style lang="scss">
$bg:#283443;
$light_gray:#fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

.inputType {
  .el-input {
    width: 100px;

    input {
      background-color: #47586e;
      border-top-width: 0px;
      border-left-width: 0px;
      border-right-width: 0px;
      border-bottom-width: 1px;
      border-radius: 0px;
    }
  }
}

/* reset element-ui css */
.login-container {
  .login-form {
    .el-input {
      display: inline-block;
      height: 47px;
      width: 85%;

      input {
        background: transparent;
        border: 0px;
        -webkit-appearance: none;
        border-radius: 0px;
        padding: 12px 5px 12px 15px;
        color: $light_gray;
        height: 47px;
        caret-color: $cursor;

        &:-webkit-autofill {
          box-shadow: 0 0 0px 1000px $bg inset !important;
          -webkit-text-fill-color: $cursor !important;
        }
      }
    }

    .el-form-item {
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(0, 0, 0, 0.1);
      border-radius: 5px;
      color: #454545;
    }
  }
}
</style>

<style lang="scss" scoped>
$bg:#47586e;
$dark_gray:#889aa4;
$light_gray:#eee;

.login-container {
  min-height: 100%;
  width: 100%;
  background-color: $bg;
  overflow: hidden;

  .paddintop {
    padding: 100px 35px 0;
  }

  .login-form {
    position: relative;
    width: 520px;
    max-width: 100%;
    margin: 0 auto;
    overflow: hidden;
  }

  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;

    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 26px;
      color: $light_gray;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
  }
}
</style>
