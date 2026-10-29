"use strict";

const STORAGE_KEY = "todolist.tasks";
const FILTERS = new Set(["all", "active", "completed"]);

const form = document.querySelector("#todo-form");
const input = document.querySelector("#todo-input");
const formError = document.querySelector("#form-error");
const list = document.querySelector("#todo-list");
const emptyState = document.querySelector("#empty-state");
const summary = document.querySelector("#summary");
const storageNotice = document.querySelector("#storage-notice");
const filterButtons = document.querySelectorAll("[data-filter]");

let tasks = [];
let currentFilter = "all";
let storageAvailable = true;
let storageHasInvalidData = false;

function isTask(value) {
  return value !== null
    && typeof value === "object"
    && typeof value.id === "string"
    && value.id.length > 0
    && typeof value.title === "string"
    && value.title.trim().length > 0
    && typeof value.completed === "boolean"
    && typeof value.createdAt === "string"
    && !Number.isNaN(Date.parse(value.createdAt));
}

function setStorageNotice(message) {
  storageNotice.textContent = message;
  storageNotice.hidden = message.length === 0;
}

function loadTasks() {
  let serialized;

  try {
    serialized = window.localStorage.getItem(STORAGE_KEY);
  } catch (error) {
    storageAvailable = false;
    setStorageNotice("브라우저 저장소에 접근할 수 없어 변경 사항은 이 페이지를 여는 동안에만 유지됩니다.");
    console.error("Todo List storage could not be read.", error);
    return [];
  }

  if (serialized === null) {
    return [];
  }

  try {
    const parsed = JSON.parse(serialized);
    if (!Array.isArray(parsed) || !parsed.every(isTask)) {
      throw new TypeError("Saved todo data does not match the expected format.");
    }

    const ids = new Set(parsed.map((task) => task.id));
    if (ids.size !== parsed.length) {
      throw new TypeError("Saved todo data contains duplicate IDs.");
    }

    return parsed;
  } catch (error) {
    storageHasInvalidData = true;
    setStorageNotice("저장된 할 일 데이터가 손상되어 목록을 비운 상태로 시작했습니다. 새로 추가한 항목을 저장하면 기존 손상 데이터는 교체됩니다.");
    console.error("Todo List storage contains invalid data.", error);
    return [];
  }
}

function saveTasks() {
  if (!storageAvailable) {
    return false;
  }

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    storageHasInvalidData = false;
    setStorageNotice("");
    return true;
  } catch (error) {
    storageAvailable = false;
    setStorageNotice("할 일은 현재 화면에 반영되었지만 브라우저 저장소 오류로 저장되지 않았습니다.");
    console.error("Todo List changes could not be saved.", error);
    return false;
  }
}

function createId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function createButton(label, className, action, accessibleName = label) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.setAttribute("aria-label", accessibleName);
  button.dataset.action = action;
  return button;
}

function renderTask(task) {
  const item = document.createElement("li");
  item.className = `todo-item${task.completed ? " is-completed" : ""}`;
  item.dataset.id = task.id;

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.className = "todo-check";
  checkbox.checked = task.completed;
  checkbox.dataset.action = "toggle";
  checkbox.setAttribute("aria-label", `${task.title} 완료`);
  item.append(checkbox);

  const title = document.createElement("span");
  title.className = "todo-title";
  title.textContent = task.title;
  item.append(title);

  const actions = document.createElement("div");
  actions.className = "item-actions";
  actions.setAttribute("role", "group");
  actions.setAttribute("aria-label", `${task.title} 작업`);
  actions.append(
    createButton("수정", "icon-button", "edit", `${task.title} 수정`),
    createButton("삭제", "icon-button delete-button", "delete", `${task.title} 삭제`),
  );
  item.append(actions);
  return item;
}

function render() {
  const visibleTasks = tasks.filter((task) => {
    if (currentFilter === "active") return !task.completed;
    if (currentFilter === "completed") return task.completed;
    return true;
  });
  const completedCount = tasks.filter((task) => task.completed).length;

  summary.textContent = `전체 ${tasks.length}개 · 완료 ${completedCount}개`;
  filterButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.filter === currentFilter));
  });

  list.replaceChildren(...visibleTasks.map(renderTask));
  if (visibleTasks.length > 0) {
    emptyState.textContent = "";
  } else if (tasks.length === 0) {
    emptyState.textContent = "아직 할 일이 없습니다. 첫 번째 할 일을 추가해 보세요.";
  } else if (currentFilter === "active") {
    emptyState.textContent = "미완료 항목이 없습니다. 모두 잘 해냈어요!";
  } else if (currentFilter === "completed") {
    emptyState.textContent = "완료한 항목이 아직 없습니다.";
  } else {
    emptyState.textContent = "표시할 할 일이 없습니다.";
  }
}

function commitTasks(nextTasks) {
  tasks = nextTasks;
  saveTasks();
  render();
}

function beginEdit(item, task) {
  const editForm = document.createElement("form");
  editForm.className = "edit-form";
  editForm.dataset.id = task.id;

  const editInput = document.createElement("input");
  editInput.className = "edit-input";
  editInput.type = "text";
  editInput.value = task.title;
  editInput.maxLength = 500;
  editInput.setAttribute("aria-label", `${task.title} 제목 수정`);

  const actions = document.createElement("div");
  actions.className = "edit-actions";
  const saveButton = document.createElement("button");
  saveButton.className = "edit-save";
  saveButton.type = "submit";
  saveButton.textContent = "저장";
  const cancelButton = createButton("취소", "edit-cancel", "cancel-edit", "수정 취소");
  actions.append(saveButton, cancelButton);
  editForm.append(editInput, actions);

  item.replaceChildren(editForm);
  editInput.focus();
  editInput.select();
}

function updateTask(id, updater) {
  const nextTasks = tasks.map((task) => (task.id === id ? updater(task) : task));
  commitTasks(nextTasks);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = input.value.trim();

  if (!title) {
    formError.textContent = "할 일 제목을 입력해 주세요.";
    input.focus();
    return;
  }

  formError.textContent = "";
  const task = {
    id: createId(),
    title,
    completed: false,
    createdAt: new Date().toISOString(),
  };
  commitTasks([...tasks, task]);
  input.value = "";
  input.focus();
});

input.addEventListener("input", () => {
  if (formError.textContent) {
    formError.textContent = "";
  }
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (!FILTERS.has(button.dataset.filter)) {
      return;
    }
    currentFilter = button.dataset.filter;
    render();
  });
});

list.addEventListener("change", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement) || target.dataset.action !== "toggle") {
    return;
  }

  const item = target.closest("[data-id]");
  const task = tasks.find((candidate) => candidate.id === item.dataset.id);
  if (task) {
    updateTask(task.id, (current) => ({ ...current, completed: target.checked }));
  }
});

list.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }

  const item = button.closest("[data-id]");
  const task = tasks.find((candidate) => candidate.id === item.dataset.id);
  if (!task) {
    return;
  }

  if (button.dataset.action === "edit") {
    beginEdit(item, task);
  } else if (button.dataset.action === "delete") {
    commitTasks(tasks.filter((candidate) => candidate.id !== task.id));
    input.focus();
  } else if (button.dataset.action === "cancel-edit") {
    render();
  }
});

list.addEventListener("submit", (event) => {
  const editForm = event.target;
  if (!(editForm instanceof HTMLFormElement) || !editForm.matches(".edit-form")) {
    return;
  }

  event.preventDefault();
  const editInput = editForm.querySelector(".edit-input");
  const title = editInput.value.trim();
  if (!title) {
    editInput.setCustomValidity("할 일 제목을 입력해 주세요.");
    editInput.reportValidity();
    return;
  }

  editInput.setCustomValidity("");
  const id = editForm.dataset.id;
  updateTask(id, (task) => ({ ...task, title }));
  const updatedItem = [...list.querySelectorAll("[data-id]")].find((item) => item.dataset.id === id);
  updatedItem?.querySelector('[data-action="edit"]')?.focus();
});

list.addEventListener("input", (event) => {
  const target = event.target;
  if (target instanceof HTMLInputElement && target.matches(".edit-input")) {
    target.setCustomValidity("");
  }
});

list.addEventListener("keydown", (event) => {
  if (event.key !== "Escape" || !event.target.matches(".edit-input")) {
    return;
  }
  event.preventDefault();
  render();
  input.focus();
});

tasks = loadTasks();
if (storageHasInvalidData) {
  storageNotice.hidden = false;
}
render();
