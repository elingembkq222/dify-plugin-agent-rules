/**
 * API 模块 - 与插件后端通信
 */

// API 基础路径 - 修改为直接调用插件API
const API_BASE = '';

/**
 * 显示通知
 * @param {string} message - 通知消息
 * @param {string} type - 通知类型 (success, error)
 */
function showToast(message, type = 'success') {
    const toastEl = document.getElementById('toast');
    const toast = new bootstrap.Toast(toastEl);
    
    // 设置通知样式
    toastEl.className = `toast ${type}`;
    
    // 设置通知内容
    const toastBody = toastEl.querySelector('.toast-body');
    toastBody.textContent = message;
    
    // 显示通知
    toast.show();
}

/**
 * 格式化日期时间
 * @param {string} dateString - 日期字符串
 * @returns {string} 格式化后的日期时间
 */
function formatDateTime(dateString) {
    if (!dateString) return '未知';
    
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 验证 JSON 格式
 * @param {string} jsonString - JSON 字符串
 * @returns {boolean} 是否为有效的 JSON
 */
function isValidJSON(jsonString) {
    try {
        JSON.parse(jsonString);
        return true;
    } catch (e) {
        return false;
    }
}

/**
 * 获取规则列表
 * @param {string} target - 目标过滤器 (可选)
 * @returns {Promise} Promise 对象
 */
function listRules(target = null) {
    // 模拟数据，实际应用中应该从后端API获取
    return new Promise((resolve) => {
        setTimeout(() => {
            const mockData = {
                success: true,
                result: {
                    rules: [
                        {
                            id: "user_validation",
                            name: "用户验证规则",
                            description: "验证用户输入的规则",
                            target: "user",
                            rule_count: 2,
                            created_at: new Date().toISOString()
                        },
                        {
                            id: "product_validation",
                            name: "产品验证规则",
                            description: "验证产品信息的规则",
                            target: "product",
                            rule_count: 3,
                            created_at: new Date().toISOString()
                        }
                    ]
                }
            };
            resolve(mockData.result);
        }, 500);
    });
    
    // 实际API调用代码（注释掉）
    /*
    const params = target ? `?target=${encodeURIComponent(target)}` : '';
    
    return fetch(`${API_BASE}/list_rules${params}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data.result;
        } else {
            throw new Error(data.error || '获取规则列表失败');
        }
    });
    */
}

/**
 * 渲染规则列表
 * @param {Array} rules - 规则列表
 */
function renderRulesList(rules) {
    const rulesListEl = document.getElementById('rulesList');
    
    if (!rules || rules.length === 0) {
        rulesListEl.innerHTML = '<div class="col-12"><div class="alert alert-info">没有找到规则</div></div>';
        return;
    }
    
    let html = '';
    rules.forEach(rule => {
        html += `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card rule-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${rule.name}</h5>
                        <p class="card-text text-muted">${rule.description || '无描述'}</p>
                        <div class="mb-2">
                            <span class="badge bg-primary">${rule.target}</span>
                            <span class="badge bg-info ms-1">${rule.rule_count} 条规则</span>
                        </div>
                        <p class="card-text">
                            <small class="text-muted">创建时间: ${formatDateTime(rule.created_at)}</small>
                        </p>
                        <div class="d-flex justify-content-between">
                            <button class="btn btn-sm btn-outline-primary view-rule" data-id="${rule.id}">
                                <i class="bi bi-eye"></i> 查看
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-rule" data-id="${rule.id}">
                                <i class="bi bi-trash"></i> 删除
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    rulesListEl.innerHTML = html;
    
    // 添加事件监听器
    document.querySelectorAll('.view-rule').forEach(btn => {
        btn.addEventListener('click', function() {
            const ruleId = this.getAttribute('data-id');
            viewRuleDetails(ruleId);
        });
    });
    
    document.querySelectorAll('.delete-rule').forEach(btn => {
        btn.addEventListener('click', function() {
            const ruleId = this.getAttribute('data-id');
            if (confirm('确定要删除这个规则集吗？')) {
                deleteRule(ruleId);
            }
        });
    });
}

/**
 * 查看规则详情
 * @param {string} ruleId - 规则 ID
 */
function viewRuleDetails(ruleId) {
    // 这里可以实现查看规则详情的功能
    showToast(`查看规则详情: ${ruleId}`, 'success');
}

/**
 * 删除规则
 * @param {string} ruleId - 规则 ID
 */
function deleteRule(ruleId) {
    // 这里可以实现删除规则的功能
    showToast(`删除规则: ${ruleId}`, 'success');
}

/**
 * 添加规则集
 * @param {Object} ruleJson - 规则集 JSON
 * @returns {Promise} Promise 对象
 */
function addRule(ruleJson) {
    // 模拟添加规则，实际应用中应该调用后端API
    return new Promise((resolve) => {
        setTimeout(() => {
            const mockResult = {
                success: true,
                result: {
                    message: "规则集添加成功",
                    id: `rule_${Date.now()}`
                }
            };
            resolve(mockResult.result);
        }, 500);
    });
    
    // 实际API调用代码（注释掉）
    /*
    return fetch(`${API_BASE}/add_rule`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rule_json: ruleJson })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data.result;
        } else {
            throw new Error(data.error || '添加规则失败');
        }
    });
    */
}

/**
 * 验证规则集
 * @param {string} rulesetId - 规则集 ID
 * @param {Object} context - 上下文数据
 * @returns {Promise} Promise 对象
 */
function validateRuleset(rulesetId, context) {
    // 模拟验证规则，实际应用中应该调用后端API
    return new Promise((resolve) => {
        setTimeout(() => {
            const mockResult = {
                success: true,
                result: {
                    pass: Math.random() > 0.5, // 随机通过或失败
                    violations: Math.random() > 0.5 ? [] : [
                        {
                            id: "age_check",
                            message: "用户年龄必须大于18岁",
                            expression: {
                                field: "age",
                                operator: "gt",
                                value: 18
                            }
                        }
                    ]
                }
            };
            resolve(mockResult.result);
        }, 500);
    });
    
    // 实际API调用代码（注释掉）
    /*
    return fetch(`${API_BASE}/validate_ruleset`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            ruleset_id: rulesetId,
            context: context
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data.result;
        } else {
            throw new Error(data.error || '验证规则失败');
        }
    });
    */
}

/**
 * 从自然语言生成规则
 * @param {string} query - 自然语言查询
 * @param {Object} context - 上下文数据结构
 * @returns {Promise} Promise 对象
 */
function generateRuleFromQuery(query, context = {}) {
    // 模拟生成规则，实际应用中应该调用后端API
    return new Promise((resolve) => {
        setTimeout(() => {
            const mockResult = {
                success: true,
                result: {
                    query: query,
                    rule: {
                        field: "age",
                        operator: "gt",
                        value: 18
                    }
                }
            };
            resolve(mockResult.result);
        }, 1000); // 模拟较长的处理时间
    });
    
    // 实际API调用代码（注释掉）
    /*
    return fetch(`${API_BASE}/generate_rule_from_query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            query: query,
            context: context
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data.result;
        } else {
            throw new Error(data.error || '生成规则失败');
        }
    });
    */
}

/**
 * 渲染验证结果
 * @param {Object} result - 验证结果
 */
function renderValidationResult(result) {
    const validationResultEl = document.getElementById('validationResult');
    
    if (!result) {
        validationResultEl.innerHTML = '<div class="alert alert-warning">没有验证结果</div>';
        return;
    }
    
    const passed = result.pass;
    const violations = result.violations || [];
    
    let html = `
        <div class="alert ${passed ? 'alert-success' : 'alert-danger'}">
            <h5 class="alert-heading">
                <i class="bi ${passed ? 'bi-check-circle-fill' : 'bi-x-circle-fill'}"></i>
                验证${passed ? '通过' : '失败'}
            </h5>
            ${violations.length > 0 ? '<p>以下规则验证失败:</p>' : '<p>所有规则验证通过</p>'}
        </div>
    `;
    
    if (violations.length > 0) {
        html += '<div class="card"><div class="card-header">违规详情</div><div class="card-body">';
        
        violations.forEach(violation => {
            html += `
                <div class="mb-3 p-3 border rounded">
                    <h6>规则 ID: ${violation.id}</h6>
                    <p class="mb-1">${violation.message}</p>
                    <div class="rule-expression">${JSON.stringify(violation.expression, null, 2)}</div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    validationResultEl.innerHTML = html;
}

/**
 * 渲染生成的规则
 * @param {Object} result - 生成结果
 */
function renderGeneratedRule(result) {
    const generatedRuleEl = document.getElementById('generatedRule');
    
    if (!result || !result.rule) {
        generatedRuleEl.innerHTML = '<div class="alert alert-warning">没有生成规则</div>';
        return;
    }
    
    const query = result.query;
    const rule = result.rule;
    
    let html = `
        <div class="card">
            <div class="card-header">
                <i class="bi bi-magic"></i> 生成的规则
            </div>
            <div class="card-body">
                <h6>原始查询</h6>
                <p class="mb-3">${query}</p>
                
                <h6>规则表达式</h6>
                <div class="rule-expression mb-3">${JSON.stringify(rule, null, 2)}</div>
                
                <button class="btn btn-primary btn-sm" id="useGeneratedRule">
                    <i class="bi bi-plus-circle"></i> 使用此规则
                </button>
            </div>
        </div>
    `;
    
    generatedRuleEl.innerHTML = html;
    
    // 添加事件监听器
    document.getElementById('useGeneratedRule').addEventListener('click', function() {
        // 切换到添加规则标签页
        const addTab = new bootstrap.Tab(document.getElementById('add-tab'));
        addTab.show();
        
        // 填充规则 JSON
        document.getElementById('ruleJson').value = JSON.stringify({
            name: `Generated Rule: ${query.substring(0, 30)}...`,
            target: "default",
            description: `Rule generated from query: ${query}`,
            rules: [
                {
                    id: rule.id || "generated_rule",
                    expression: rule,
                    message: "Generated rule validation failed"
                }
            ]
        }, null, 2);
    });
}

/**
 * 初始化页面
 */
document.addEventListener('DOMContentLoaded', function() {
    // 加载规则列表
    loadRulesList();
    
    // 刷新按钮
    document.getElementById('refreshBtn').addEventListener('click', loadRulesList);
    
    // 过滤按钮
    document.getElementById('filterBtn').addEventListener('click', function() {
        const target = document.getElementById('targetFilter').value;
        loadRulesList(target);
    });
    
    // 添加规则表单
    document.getElementById('addRuleForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const ruleJson = document.getElementById('ruleJson').value;
        
        if (!isValidJSON(ruleJson)) {
            showToast('规则 JSON 格式无效', 'error');
            return;
        }
        
        const ruleData = JSON.parse(ruleJson);
        
        addRule(ruleData)
            .then(result => {
                showToast(result.message, 'success');
                this.reset();
                loadRulesList();
            })
            .catch(error => {
                showToast(error.message, 'error');
            });
    });
    
    // 验证规则表单
    document.getElementById('validateRuleForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const rulesetId = document.getElementById('rulesetId').value;
        const contextData = document.getElementById('contextData').value;
        
        if (!isValidJSON(contextData)) {
            showToast('上下文数据 JSON 格式无效', 'error');
            return;
        }
        
        const context = JSON.parse(contextData);
        
        validateRuleset(rulesetId, context)
            .then(result => {
                renderValidationResult(result);
            })
            .catch(error => {
                showToast(error.message, 'error');
            });
    });
    
    // 生成规则表单
    document.getElementById('generateRuleForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const query = document.getElementById('naturalQuery').value;
        const contextData = document.getElementById('queryContext').value;
        
        let context = {};
        if (contextData && isValidJSON(contextData)) {
            context = JSON.parse(contextData);
        }
        
        generateRuleFromQuery(query, context)
            .then(result => {
                renderGeneratedRule(result);
            })
            .catch(error => {
                showToast(error.message, 'error');
            });
    });
});

/**
 * 加载规则列表
 * @param {string} target - 目标过滤器 (可选)
 */
function loadRulesList(target = null) {
    listRules(target)
        .then(result => {
            renderRulesList(result.rules);
            
            // 更新验证规则表单的规则集选项
            updateRulesetOptions(result.rules);
        })
        .catch(error => {
            showToast(error.message, 'error');
        });
}

/**
 * 更新规则集选项
 * @param {Array} rules - 规则列表
 */
function updateRulesetOptions(rules) {
    const rulesetIdEl = document.getElementById('rulesetId');
    
    // 清空现有选项
    rulesetIdEl.innerHTML = '<option value="">选择规则集...</option>';
    
    // 添加新选项
    rules.forEach(rule => {
        const option = document.createElement('option');
        option.value = rule.id;
        option.textContent = `${rule.name} (${rule.target})`;
        rulesetIdEl.appendChild(option);
    });
}