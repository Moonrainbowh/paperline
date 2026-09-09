const $ = s => document.querySelector(s);
const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data, view = 'overview', filter = '', query = '';
const titles = {overview:'流水线总览',modules:'能力与文档',checks:'质量校验',runs:'运行记录',gaps:'待建设环节'};
const stages = [
  ['P1','研究证据画像','整理研究边界、文献与主张，建立可追溯的证据地图。','工作流已定义','paper-navigator/references/research-context-passport.md'],
  ['P2','选刊与规则锁定','硬门筛选、双轨写作画像，确认期刊并锁定契约。','工作流 + 校验器','journal-navigator/SKILL.md'],
  ['P3','中文全文定稿','19 步写作流程推进至 S6，经作者确认锁定 S7。','工作流 + 状态校验','paper-navigator/references/manuscript-finalization-workflow.md'],
  ['P4','忠实学术英译','术语治理、多格式处理、译文完整性与交接审计。','工作流 + 审计脚本','zh-en-paper-translator/SKILL.md'],
  ['P5','投稿前检查','核对期刊、版本和交接材料，检查投稿前风险。','工作流 + 交接校验','paper-navigator/references/review-risk-audit.md']
];
const gaps = [
  ['任务执行与模型接入','待实现','将 Skill 指令转换为可运行任务；需要模型调用、任务队列、日志、取消与失败恢复。当前 UI 可运行确定性校验。'],
  ['真实论文项目与产物管理','待实现','需要项目创建、材料导入、产物版本关联和阶段操作；已有状态合同与校验器，尚无完整项目服务。'],
  ['作者确认与状态推进','待实现','需要针对确切版本确认期刊、S7 和交接，驱动失效传播。当前页面不代替作者确认。'],
  ['科学绘图执行链','待实现','已有图表规划与 QA 文档；仍需图表注册表、Python 渲染、导出、视觉检查及稿件嵌入。'],
  ['检索、全文与文档工具连接','依赖宿主','已有工作流与 DOI 记录；浏览器、机构全文访问、DOCX/PDF/OCR 需宿主能力接入，仓库没有独立端到端服务。'],
  ['真实论文端到端验收','待验证','需要一篇授权论文走通 P1–P5，核验论文、图表、引用、版本与人工确认；合成合同演练不能替代真实验收。'],
  ['完整应用交付包','待实现','dist 中为早期单 Skill 压缩包；尚需覆盖四个 Skill 与 Web UI 的统一发布、安装及升级方式。']
];
async function api(path, options) { const r = await fetch(path, options); const body = await r.json(); if (!r.ok) throw Error(body.error || `HTTP ${r.status}`); return body; }
function toast(text) { $('#toast').textContent=text; $('#toast').style.display='block'; setTimeout(()=>$('#toast').style.display='none',3500); }
function hero(kicker,title,desc) { return `<section class="hero"><div><div class="eyebrow">${kicker}</div><h1>${title}</h1><p>${desc}</p></div><div class="hero-mark" aria-hidden="true">p →</div></section>`; }
function fileButton(path,label) { return `<button class="link" data-file="${escape(path)}">${escape(label)} ↗</button>`; }
function overview() {
  const scripts=data.files.filter(x=>x.endsWith('.py')).length;
  return hero('THE RESEARCH PIPELINE','让研究的每一步，都有据可循。','从研究证据到投稿前检查，汇集流程、工具与下一步建设方向。') +
  `<div class="metrics"><div class="metric">专业与编排 Skills<strong>${data.skills.length.toString().padStart(2,'0')}</strong><small>源码目录实时盘点</small></div><div class="metric">主线阶段<strong>05</strong><small>中文定稿优先 · P1–P5</small></div><div class="metric">Python 工具<strong>${scripts.toString().padStart(2,'0')}</strong><small>校验、审计与合同演练</small></div><div class="metric">真实全流程验收<strong>—</strong><small>尚无完整验收证据</small></div></div>
  <div class="section-head"><h2>从证据到论文</h2><span>流程覆盖 ≠ 自动执行完成</span></div><div class="stages">${stages.map(s=>`<article class="stage"><div class="num">${s[0]}<span>→</span></div><h3>${s[1]}</h3><p>${s[2]}</p><span class="pill">${s[3]}</span><br>${fileButton(s[4],'查看阶段依据')}</article>`).join('')}</div>
  <div class="notice">人工确认门：期刊契约锁定 + 中文 S7 作者确认后，才能进入正式英译。期刊未定时，经授权可先推进通用中文稿至 S6。</div>
  <div class="columns"><section class="panel"><div class="section-head" style="margin-top:0"><h2>已具备的基础</h2><button class="link" data-go="modules">全部文档 ↗</button></div>${[
    ['研究与写作','文献检索、全文获取、阅读、证据链、章节写作与审稿回复','paper-navigator/SKILL.md'],
    ['版本与交接合同','阶段依赖、作者确认门、版本绑定与上游变更失效规则','paperline/references/pipeline-contract.md'],
    ['确定性质量检查','运行现有校验器，查看真实退出码与完整输出','paperline/scripts/run_contract_dry_run.py']
  ].map(x=>`<div class="row"><div><h3>${fileButton(x[2],x[0])}</h3><p>${x[1]}</p></div><span class="arrow">↗</span></div>`).join('')}</section>
  <section class="panel"><div class="section-head" style="margin-top:0"><h2>下一步，把流程变成执行</h2><button class="link" data-go="gaps">查看缺口 ↗</button></div>${gaps.slice(0,3).map((g,i)=>`<div class="gap"><span class="gap-index">0${i+1}</span><div><h3>${g[0]}</h3><p>${g[2]}</p></div></div>`).join('')}</section></div>`;
}
function modules() {
  return hero('CAPABILITY LIBRARY','能力与文档','浏览仓库中的真实文件；搜索流程、参考资料与执行脚本。')+`<input id="search" aria-label="搜索文件" placeholder="搜索文件名，例如 pipeline、figure、translation…" value="${escape(query)}"><div class="filters">${['',...data.skills].map(x=>`<button data-filter="${x}" class="${filter===x?'active':''}">${x||'全部模块'}</button>`).join('')}</div><div class="filelist" id="filelist">${fileRows()}</div>`;
}
function fileRows(){ const list=data.files.filter(x=>(!filter||x.startsWith(filter+'/'))&&x.toLowerCase().includes(query.toLowerCase())); return list.map(x=>`<button class="file" data-file="${escape(x)}"><span>${escape(x.split('/').pop())}</span><small>${escape(x)}</small></button>`).join('')||'<p class="empty">没有匹配文件，请调整关键词。</p>'; }
const statusText={idle:'未运行',running:'运行中…',passed:'通过',failed:'未通过'};
function checks(){return hero('QUALITY GATES','运行检查，留下证据。','执行本地 Python 校验器。自测及合成演练通过，不代表真实稿件完成验收。')+`<section class="panel">${data.checks.map(c=>`<div class="row"><div><h3>${c.title}</h3><small>${escape(c.path)}</small>${c.finished_at?`<p>本次服务运行 · ${new Date(c.finished_at).toLocaleString()}</p>`:''}</div><div class="actions"><span class="status ${c.status}">${statusText[c.status]}</span>${c.output!==undefined?`<button data-log="${c.id}">查看输出</button>`:''}<button data-check="${c.id}" ${data.checks.some(c=>c.status==='running')?'disabled':''}>运行校验</button></div></div>`).join('')}</section><p class="sub">结果保留在当前服务内存中，重启后显示为未运行。</p>`;}
function runs(){return hero('RUN ARCHIVE','已有运行记录','读取 runs 目录中的记录文件，保留其实际证据范围。')+`<div class="notice">当前发现 ${data.runs.length} 份检索记录、${data.states.length} 份 pipeline-state.json。DOI 记录只证明记录存在，不代表 PDF 获取、阅读或论文阶段完成。</div><section class="panel">${data.runs.map(r=>`<div class="row"><div><h3>${escape(r.name)}</h3><p>${escape(r.error||JSON.stringify(r.records))}</p></div>${r.path?fileButton(r.path,'原始记录'):''}</div>`).join('')||'<p class="empty">尚无运行记录。</p>'}</section>`;}
function missing(){return hero('BUILD ROADMAP','已经有骨架，还需要执行闭环。','以下为当前源码盘点得出的应用建设缺口，按建议优先顺序排列。')+`<section class="panel">${gaps.map((g,i)=>`<div class="row"><div><h3><span class="gap-index">0${i+1}</span>${g[0]}</h3><p>${g[2]}</p></div><span class="pill amber">${g[1]}</span></div>`).join('')}</section>`;}
function render(){ $('#breadcrumb').textContent=titles[view]; document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b.dataset.view===view)); $('#app').innerHTML=({overview,modules,checks,runs,gaps:missing}[view])(); }
function reader(title,content){$('#reader-title').textContent=title;$('#reader-body').textContent=content;$('#reader').showModal();}
async function refresh(){data=await api('/api/overview');render();}
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;try{
 if(b.dataset.view||b.dataset.go){view=b.dataset.view||b.dataset.go;render();}
 if(b.dataset.filter!==undefined){filter=b.dataset.filter;render();}
 if(b.dataset.file){const f=await api('/api/file?path='+encodeURIComponent(b.dataset.file));reader(f.path,f.content);}
 if(b.dataset.log){const c=data.checks.find(c=>c.id===b.dataset.log);reader(c.title+` · exit ${c.exit_code??'unknown'}`,c.output);}
 if(b.dataset.check){await api('/api/checks/'+b.dataset.check,{method:'POST',headers:{'X-Paperline':'workbench'}});await refresh();}
 if(b.id==='refresh'){await refresh();toast('已刷新本地源码');}
 if(b.id==='close-reader')$('#reader').close();
 }catch(error){toast(error.message);}});
document.addEventListener('input',e=>{if(e.target.id==='search'){query=e.target.value;$('#filelist').innerHTML=fileRows();}});
setInterval(async()=>{if(data?.checks.some(c=>c.status==='running')){try{data=await api('/api/overview');if(view==='checks')render();}catch(e){toast('服务连接中断：'+e.message);}}},1500);
refresh().catch(e=>{$('#app').textContent='读取仓库失败：'+e.message;});
