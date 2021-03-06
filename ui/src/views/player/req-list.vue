<template lang="pug">
  .app-container
    .filter-container
      el-tooltip(content="可筛选玩家名、IP、QQ", effect="dark", placement="bottom")
        el-input.filter-item(v-model="listQuery.keyword", placeholder="请输入关键字", style="width: 200px;", @keyup.enter.native="getList")
      el-select.filter-item(v-model="listQuery.status", style={ 'margin-left': '8px' })
        el-option(key="", label="任意", value="")
        el-option(v-for="(v, k) in statuses", :key="k", :label="v", :value="k")
      el-button.filter-item(v-waves, style={ 'margin-left': '8px' }, type="primary", icon="el-icon-search", @click="getList")

    el-table(
      v-loading="listLoading",
      :data="list",
      border,
      fit,
      highlight-current-row,
      style="width: 100%;",
      @cell-dblclick="row => row.edit = true"
    )
      el-table-column(label="玩家名", prop="player_name", align="center")
      el-table-column(label="申请时间", align="center", width="160px")
        template(slot-scope="{row}")
          span {{ row.req_time | timestampFilter }}
      el-table-column(label="审核人", prop="apply_op", align="center")
      el-table-column(label="审核时间", align="center", width="160px")
        template(slot-scope="{row}")
          span {{ row.apply_time | timestampFilter }}
      el-table-column(label="状态", align="center", width="80px")
        template(slot-scope="{row}")
          span {{ row.status | statusFilter }}
      el-table-column(label="申请类型", align="center", width="120px")
        template(slot-scope="{row}")
          span {{ row.type | typeFilter }}
      el-table-column(label="IP", prop="ip", align="center", width="130px")
      el-table-column(label="QQ", prop="qq", align="center", width="100px")
      el-table-column(align="center")
        template(slot="header")
          el-tooltip(content="对于老玩家邀请，此处为邀请人，对于 OP 线下沟通，此处为 OP 名", effect="dark", placement="bottom")
            label 关系人&nbsp;
              i.el-icon-info
        template(slot-scope="{row}")
          span {{ row.type === 'Invite' ? row.old_player_name : row.op_name }}
      el-table-column(label="审批", align="center", width="140px")
        template(slot-scope="{row}")
          el-button(v-if="row.status === 'NEW'", size="mini", type="success", icon="el-icon-check", @click="handleApply(row, 'ACCEPT')")
          el-button(v-if="row.status === 'NEW'", size="mini", type="warning", icon="el-icon-close", @click="handleApply(row, 'DENY')")

    pagination(v-show="total>0", :total="total", :page.sync="listQuery.page", :limit.sync="listQuery.pageSize", @pagination="getList")
</template>

<script>
import { fetchReqList, apply } from '@/api/req'
import { notifySuccess } from '@/utils/notify'
import Pagination from '@/components/Pagination'

const types = {
  QQLevel: 'QQ 等级过太阳',
  Invite: '老玩家邀请',
  PYJY: 'OP 线下沟通'
}
const statuses = {
  NEW: '待处理',
  ACCEPT: '已通过',
  DENY: '已拒绝'
}

export default {
  name: 'ReqList',
  components: { Pagination },
  filters: {
    typeFilter(val) {
      return types[val]
    },
    statusFilter(val) {
      return statuses[val]
    }
  },
  data() {
    return {
      listQuery: {
        keyword: '',
        status: '',
        page: 1,
        pageSize: 20
      },
      list: [],
      total: 0,
      listLoading: true,
      types,
      statuses
    }
  },
  mounted() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchReqList(this.listQuery).then(response => {
        this.list = response.data.list
        this.total = response.data.totalRow
        this.listQuery.page = response.data.page

        // 取消加载动画
        setTimeout(() => {
          this.listLoading = false
        }, 100)
      })
    },
    handleApply(row, result) {
      this.$confirm(
        '您确实要审核' + (result === 'ACCEPT' ? '通过' : '不通过') + '么？', '审核确认', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        apply({
          id: row.id,
          result
        }).then(response => {
          notifySuccess(result === 'ACCEPT' ? '审核成功，已自动为其创建账号' : '拒绝成功')

          row.status = result
        })
      })
    }
  }
}
</script>
