"use strict";

const RESULTS = Object.freeze({ON_TIME: "准时", DELAYED: "延误", IN_TRANSIT: "在途", CANCELLED: "已取消", MISSING_TIMESTAMP: "时间缺失"});
const numberFormat = new Intl.NumberFormat("zh-CN");
const shanghaiFormat = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai", year: "numeric", month: "2-digit", day: "2-digit",
  hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23"
});
const count = value => numberFormat.format(value);
const rate = value => value === null ? "N/A" : `${value.toFixed(2)}%`;
function formatTime(value) {
  if (value === null) return "—";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) throw new Error("查询响应中的时间格式无效，请重试。");
  return `${shanghaiFormat.format(date)}（上海）`;
}
function trendMaximum(days) {
  return Math.max(3, Math.ceil(days.reduce((highest, day) => Math.max(highest, day.total_count), 0) / 3) * 3);
}
function trendGeometry(days) {
  const max = trendMaximum(days);
  return days.map((day, index) => ({
    x: days.length === 1 ? 320 : 48 + index / (days.length - 1) * 544,
    y: 170 - day.total_count / max * 140,
    date: day.shipment_date, value: day.total_count
  }));
}
function validateDashboard(data, carrier) {
  const fail = () => { throw new Error("查询响应格式无效，请重试。"); };
  const integer = value => Number.isSafeInteger(value) && value >= 0;
  const text = value => typeof value === "string";
  const metrics = value => value && ["total_count", "eligible_count", "on_time_count", "delayed_count", "excluded_count"].every(key => integer(value[key])) &&
    value.on_time_count + value.delayed_count === value.eligible_count && value.eligible_count + value.excluded_count === value.total_count &&
    (value.eligible_count === 0 ? value.on_time_rate === null : typeof value.on_time_rate === "number" && Number.isFinite(value.on_time_rate) && value.on_time_rate >= 0 && value.on_time_rate <= 100);
  if (!data || data.scope?.carrier !== carrier || !metrics(data.summary) ||
    !["carriers", "by_carrier", "daily", "shipments"].every(key => Array.isArray(data[key]))) fail();
  if (!data.carriers.every(row => text(row.carrier_id) && text(row.carrier_name)) ||
    !data.by_carrier.every(row => text(row.carrier_id) && text(row.carrier_name) && metrics(row))) fail();
  const datePattern = /^\d{4}-\d{2}-\d{2}$/;
  if (!data.daily.every(row => text(row.shipment_date) && datePattern.test(row.shipment_date) && integer(row.total_count))) fail();
  if (data.daily.reduce((sum, row) => sum + row.total_count, 0) !== data.summary.total_count) fail();
  for (let index = 1; index < data.daily.length; index++) {
    if (Date.parse(data.daily[index].shipment_date) - Date.parse(data.daily[index - 1].shipment_date) !== 86400000) fail();
  }
  const timestamp = value => text(value) && value.endsWith("Z") && Number.isFinite(Date.parse(value));
  const nullableTime = value => value === null || timestamp(value);
  const nullableText = value => value === null || text(value);
  const p = data.pagination;
  if (!p || p.page_size !== 20 || !integer(p.page) || p.page < 1 || !integer(p.total_pages) ||
    p.total_count !== data.summary.total_count || p.total_pages !== Math.ceil(p.total_count / 20) ||
    p.page > Math.max(1, p.total_pages) || data.shipments.length !== Math.min(20, Math.max(0, p.total_count - (p.page - 1) * 20))) fail();
  if (!data.shipments.every(row => text(row.shipment_id) && text(row.carrier_id) && text(row.carrier_name) &&
    text(row.shipment_date) && datePattern.test(row.shipment_date) && nullableText(row.origin_city) && nullableText(row.destination_city) &&
    nullableTime(row.planned_arrival) && nullableTime(row.actual_arrival) &&
    Object.hasOwn(RESULTS, row.result) && ["DELIVERED", "IN_TRANSIT", "CANCELLED"].includes(row.status))) fail();
  if (!nullableTime(data.source_snapshot_at) || !timestamp(data.queried_at)) fail();
  return data;
}

function startDashboard() {
  const $ = id => document.getElementById(id);
  let sequence = 0;
  let controller;
  let targetPage = 1;
  let pagination = null;
  const element = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const svgElement = (tag, attributes, text) => {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
    if (text !== undefined) node.textContent = text;
    return node;
  };
  function scopeLabel(carrier) {
    if (!carrier) return "全部承运商";
    const option = Array.from($("carrier").options).find(item => item.value === carrier);
    return option ? option.textContent : carrier;
  }
  function renderOptions(data) {
    const options = [new Option("全部承运商", "")];
    data.carriers.forEach(row => options.push(new Option(`${row.carrier_name || row.carrier_id} · ${row.carrier_id}`, row.carrier_id)));
    if (data.scope.carrier && !data.carriers.some(row => row.carrier_id === data.scope.carrier)) {
      options.push(new Option(data.scope.carrier, data.scope.carrier));
    }
    $("carrier").replaceChildren(...options);
    $("carrier").value = data.scope.carrier;
  }
  function renderComparison(rows) {
    const fragment = document.createDocumentFragment();
    rows.forEach(row => {
      const wrapper = element("div", undefined, "bar-row");
      const name = element("div", row.carrier_name || row.carrier_id, "bar-name");
      name.append(element("small", row.carrier_id));
      const track = element("div", undefined, `track${row.on_time_rate === null ? " unavailable" : ""}`);
      track.setAttribute("aria-hidden", "true");
      if (row.on_time_rate !== null) {
        const bar = element("div", undefined, "bar");
        bar.style.width = `${row.on_time_rate}%`;
        track.append(bar);
      }
      const value = element("div", rate(row.on_time_rate), "bar-value");
      const detail = element("small", `${count(row.on_time_count)} / ${count(row.eligible_count)}`);
      detail.setAttribute("aria-label", `准时 ${count(row.on_time_count)} 单，有效 ${count(row.eligible_count)} 单`);
      value.append(detail);
      wrapper.append(name, track, value);
      fragment.append(wrapper);
    });
    $("carrier-chart").replaceChildren(rows.length ? fragment : element("p", "无记录", "empty"));
  }
  function renderTrend(days) {
    $("daily-body").replaceChildren();
    $("trend-values").hidden = days.length === 0;
    if (!days.length) {
      $("trend-chart").replaceChildren(element("p", "无记录", "empty"));
      $("trend-description").textContent = "当前范围没有业务日期";
      return;
    }
    const points = trendGeometry(days);
    const max = trendMaximum(days);
    const chart = svgElement("svg", {viewBox: "0 0 620 210", class: "trend", role: "img", "aria-label": `每日运输单量，${days[0].shipment_date} 至 ${days.at(-1).shipment_date}。完整数据可展开下方每日单量数据。`});
    for (let index = 0; index < 4; index++) {
      const y = 170 - index / 3 * 140;
      chart.append(svgElement("path", {d: `M48 ${y}H592`, stroke: "#dbe5ed", fill: "none"}));
      chart.append(svgElement("text", {x: 40, y: y + 4, "text-anchor": "end"}, count(Math.ceil(max * index / 3))));
    }
    if (points.length > 1) {
      const coords = points.map(point => `${point.x},${point.y}`).join(" ");
      chart.append(svgElement("polygon", {points: `${points[0].x},170 ${coords} ${points.at(-1).x},170`, fill: "#eaf2f5"}));
      chart.append(svgElement("polyline", {points: coords, fill: "none", stroke: "#087f86", "stroke-width": 3, "stroke-linejoin": "round"}));
    }
    points.forEach(point => {
      const dot = svgElement("circle", {cx: point.x, cy: point.y, r: points.length === 1 ? 5 : 3, fill: "#087f86"});
      dot.append(svgElement("title", {}, `${point.date}：${count(point.value)} 单`));
      chart.append(dot);
    });
    const indices = [...new Set([0, Math.floor((days.length - 1) / 3), Math.floor((days.length - 1) * 2 / 3), days.length - 1])];
    indices.forEach(index => chart.append(svgElement("text", {x: points[index].x, y: 197, "text-anchor": "middle"}, points[index].date.slice(5))));
    $("trend-chart").replaceChildren(chart);
    $("trend-description").textContent = `${days[0].shipment_date} 至 ${days.at(-1).shipment_date} · 缺失自然日补零`;
    const fragment = document.createDocumentFragment();
    days.forEach(day => {
      const row = element("tr");
      row.append(element("td", day.shipment_date), element("td", count(day.total_count)));
      fragment.append(row);
    });
    $("daily-body").append(fragment);
  }
  function renderShipments(data) {
    const fragment = document.createDocumentFragment();
    data.shipments.forEach(shipment => {
      const row = element("tr");
      const carrier = element("td", shipment.carrier_name || shipment.carrier_id, "carrier-cell");
      carrier.append(element("small", shipment.carrier_id));
      const result = element("td");
      result.append(element("span", RESULTS[shipment.result], `result ${shipment.result}`));
      row.append(element("td", shipment.shipment_id), carrier, element("td", shipment.shipment_date),
        element("td", `${shipment.origin_city || "—"} → ${shipment.destination_city || "—"}`),
        element("td", formatTime(shipment.planned_arrival)), element("td", formatTime(shipment.actual_arrival)), result);
      fragment.append(row);
    });
    if (!data.shipments.length) {
      const row = element("tr");
      const cell = element("td", "无记录", "no-records");
      cell.colSpan = 7;
      row.append(cell);
      fragment.append(row);
    }
    $("shipments-body").replaceChildren(fragment);
    pagination = data.pagination;
    targetPage = pagination.page;
    $("page-info").textContent = pagination.total_count === 0 ? "无记录 · 共 0 单" : `第 ${pagination.page} 页 / 共 ${pagination.total_pages} 页 · 共 ${count(pagination.total_count)} 单`;
    $("previous").disabled = pagination.page <= 1 || pagination.total_pages === 0;
    $("next").disabled = pagination.page >= pagination.total_pages;
  }
  function render(data) {
    renderOptions(data);
    $("scope").textContent = scopeLabel(data.scope.carrier);
    const summary = data.summary;
    [["total-count", "total_count"], ["eligible-count", "eligible_count"], ["delayed-count", "delayed_count"],
      ["on-time-count", "on_time_count"], ["method-eligible", "eligible_count"], ["excluded-count", "excluded_count"]]
      .forEach(([id, key]) => { $(id).textContent = count(summary[key]); });
    $("on-time-rate").textContent = rate(summary.on_time_rate);
    $("rate-detail").textContent = `${count(summary.on_time_count)} 张准时 / ${count(summary.eligible_count)} 张有效`;
    renderComparison(data.by_carrier);
    renderTrend(data.daily);
    renderShipments(data);
    [["snapshot", data.source_snapshot_at], ["queried", data.queried_at]].forEach(([id, value]) => {
      $(id).textContent = formatTime(value);
      if (value === null) $(id).removeAttribute("datetime");
      else $(id).setAttribute("datetime", value);
    });
    $("empty").hidden = summary.total_count !== 0;
  }
  async function query(page = 1) {
    const request = ++sequence;
    if (controller) controller.abort();
    controller = new AbortController();
    const signal = controller.signal;
    const carrier = $("carrier").value;
    targetPage = page;
    $("scope").textContent = scopeLabel(carrier);
    $("results").hidden = true;
    $("error").hidden = true;
    $("loading").hidden = false;
    $("results").setAttribute("aria-busy", "true");
    $("status").textContent = `正在查询${scopeLabel(carrier)}，目标第 ${page} 页。`;
    try {
      const params = new URLSearchParams({carrier, page: String(page)});
      const response = await fetch(`/api/dashboard?${params}`, {signal, cache: "no-store", headers: {Accept: "application/json"}});
      if (request !== sequence) return;
      let data;
      try { data = await response.json(); }
      catch { throw new Error("查询未完成，服务器响应无效，请重试。"); }
      if (request !== sequence) return;
      if (!response.ok) {
        const safeError = [400, 502].includes(response.status) && typeof data?.error === "string" && data.error.trim();
        const error = new Error(safeError ? data.error : "查询未完成，请稍后重试。");
        error.inputError = response.status === 400;
        throw error;
      }
      render(validateDashboard(data, carrier));
      $("results").hidden = false;
      $("status").textContent = data.summary.total_count === 0 ? "查询完成，当前范围无记录。" : `查询完成，共 ${count(data.summary.total_count)} 单，第 ${data.pagination.page} 页。`;
    } catch (error) {
      if (request !== sequence) return;
      $("results").hidden = true;
      $("error-title").textContent = error.inputError ? "输入错误" : "查询失败";
      $("error-message").textContent = error instanceof TypeError ? "网络连接失败，请检查连接后重试。" : error.message || "查询未完成，请稍后重试。";
      $("error").hidden = false;
      $("status").textContent = "查询失败，可重试当前筛选与目标页。";
    } finally {
      if (request === sequence) {
        $("loading").hidden = true;
        $("results").setAttribute("aria-busy", "false");
      }
    }
  }
  $("carrier").addEventListener("change", () => query(1));
  $("clear").addEventListener("click", () => { $("carrier").value = ""; query(1); });
  $("refresh").addEventListener("click", () => query(1));
  $("retry").addEventListener("click", () => query(targetPage));
  $("previous").addEventListener("click", () => { if (pagination?.page > 1) query(pagination.page - 1); });
  $("next").addEventListener("click", () => { if (pagination && pagination.page < pagination.total_pages) query(pagination.page + 1); });
  query(1);
}

if (typeof module !== "undefined" && module.exports) module.exports = {rate, formatTime, trendGeometry, validateDashboard};
if (typeof document !== "undefined") startDashboard();
