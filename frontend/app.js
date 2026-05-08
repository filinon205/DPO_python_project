const API = 'http://localhost:8000'

const fmt = n => Math.round(n).toLocaleString('ru-RU') + ' ₽'

function switchTab(name, clickedTab) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'))
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'))
  document.getElementById('tab-' + name).classList.add('active')
  clickedTab.classList.add('active')
}

// Инициализируем Choices на select категории
const choicesCategory = new Choices('#category-select', {
  searchEnabled: true,
  searchPlaceholderValue: 'Поиск категории...',
  noResultsText: 'Ничего не найдено',
  noChoicesText: 'Нет доступных категорий',
  itemSelectText: '',
  allowHTML: false,
})

async function loadCategories(type) {
  const res = await fetch(API + '/categories/')
  const all = await res.json()

  // Собираем группы: родитель → дочерние
  const parents = all.filter(c => c.type === type && c.parent_id === null)

  // Строим массив в формате который понимает Choices.js с группами
  const grouped = []

  parents.forEach(parent => {
    const children = all.filter(c => c.parent_id === parent.id)

    if (children.length > 0) {
      // Расходы: добавляем группу с дочерними
      grouped.push({
        label: parent.name,
        id: parent.id,
        choices: children.map(c => ({
          label: c.name,
          value: String(c.id),
        }))
      })
    } else {
      // Доходы: без группы, просто пункт
      grouped.push({
        label: '',
        id: parent.id,
        choices: [{
          label: parent.name,
          value: String(parent.id),
        }]
      })
    }
  })

  choicesCategory.clearStore()
  choicesCategory.setChoices(
    grouped,
    'value',
    'label',
    true
  )
}

document.getElementById('type-select').addEventListener('change', (e) => {
  loadCategories(e.target.value)
  const isTransfer = e.target.value === 'transfer'
  document.getElementById('to-account-label').style.display = isTransfer ? '' : 'none'
  document.getElementById('to-account-select').required = isTransfer
})

loadCategories('income')

// Счета в select формы транзакции
async function loadAccountsSelect() {
  const res = await fetch(API + '/accounts/')
  const data = await res.json()
  const makeOptions = select => {
    select.innerHTML = '<option value="">— выберите —</option>'
    data.forEach(a => {
      const option = document.createElement('option')
      option.value = a.id
      option.textContent = a.name + ' (' + fmt(a.balance) + ')'
      select.appendChild(option)
    })
  }
  makeOptions(document.getElementById('account-select'))
  makeOptions(document.getElementById('to-account-select'))
}

loadAccountsSelect()

// Список счетов на вкладке Счета
async function loadAccountsList() {
  const res = await fetch(API + '/accounts/')
  const data = await res.json()
  const list = document.getElementById('accounts-list')
  list.innerHTML = ''
  if (data.length === 0) {
    list.innerHTML = '<p style="color:#888; font-size:14px;">Счетов пока нет</p>'
    return
  }
  data.forEach(a => {
    const item = document.createElement('div')
    item.className = 'account-item'
    item.innerHTML = `<span class="account-name">${a.name}</span><span class="account-balance">${fmt(a.balance)}</span>`
    list.appendChild(item)
  })
}

// Внешние фильтры
let activeTypes = new Set(['income', 'expense', 'transfer', 'debt'])
let categorySearch = ''

document.querySelectorAll('#type-filters .tag').forEach(tag => {
  tag.addEventListener('click', () => {
    const val = tag.dataset.value
    if (activeTypes.has(val)) {
      activeTypes.delete(val)
      tag.classList.remove('active')
    } else {
      activeTypes.add(val)
      tag.classList.add('active')
    }
    grid.onFilterChanged()
  })
})

document.getElementById('category-filter').addEventListener('input', e => {
  categorySearch = e.target.value.toLowerCase()
  grid.onFilterChanged()
})

// AG Grid
const columnDefs = [
  { field: 'id',              headerName: 'ID',              width: 70 },
  { field: 'date',            headerName: 'Дата',            width: 120, filter: 'agDateColumnFilter' },
  { field: 'type',            headerName: 'Тип',             width: 110 },
  { field: 'amount',          headerName: 'Сумма',           width: 140, valueFormatter: p => p.value != null ? fmt(p.value) : '' },
  { field: 'account_name',    headerName: 'Счёт источник',   width: 160 },
  { field: 'to_account_name', headerName: 'Счёт получатель', width: 160 },
  { field: 'category_name',   headerName: 'Категория',       width: 200 },
  { field: 'description',     headerName: 'Описание',        flex: 1 },
]

const gridOptions = {
  columnDefs: columnDefs,
  rowData: [],
  defaultColDef: { sortable: true, filter: true, resizable: true },
  isExternalFilterPresent: () => true,
  doesExternalFilterPass: row => {
    const typeOk = activeTypes.has(row.data.type)
    const catOk  = !categorySearch || (row.data.category_name || '').toLowerCase().includes(categorySearch)
    return typeOk && catOk
  },
}

const grid = agGrid.createGrid(document.getElementById('myGrid'), gridOptions)

async function loadTransactions() {
  const res = await fetch(API + '/transactions/')
  const data = await res.json()
  grid.setGridOption('rowData', data)
}

loadTransactions()

// Форма транзакции
document.getElementById('transaction-form').addEventListener('submit', async (e) => {
  e.preventDefault()
  const fd = new FormData(e.target)
  const payload = {
    type:          fd.get('type'),
    amount:        parseFloat(fd.get('amount')),
    date:          fd.get('date'),
    description:   fd.get('description') || null,
    account_id:    parseInt(fd.get('account_id')),
    to_account_id: fd.get('to_account_id') ? parseInt(fd.get('to_account_id')) : null,
    category_id:   fd.get('category_id') ? parseInt(fd.get('category_id')) : null,
    periodicity:   'one_time',
  }
  const res = await fetch(API + '/transactions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const msg = document.getElementById('form-message')
  if (res.ok) {
    msg.style.color = '#16a34a'
    msg.textContent = 'Транзакция сохранена!'
    e.target.reset()
    loadCategories('income')
    loadTransactions()
    loadAccountsSelect()
  } else {
    msg.style.color = '#dc2626'
    msg.textContent = 'Ошибка при сохранении'
  }
})

// Форма счёта
document.getElementById('account-form').addEventListener('submit', async (e) => {
  e.preventDefault()
  const fd = new FormData(e.target)
  const payload = {
    name:    fd.get('name'),
    balance: parseFloat(fd.get('balance')),
  }
  const res = await fetch(API + '/accounts/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const msg = document.getElementById('account-message')
  if (res.ok) {
    msg.style.color = '#16a34a'
    msg.textContent = 'Счёт создан!'
    e.target.reset()
    loadAccountsList()
    loadAccountsSelect()
  } else {
    msg.style.color = '#dc2626'
    msg.textContent = 'Ошибка при создании счёта'
  }
})

// Аналитика
async function loadAnalytics() {
  const year  = document.getElementById('year').value
  const month = document.getElementById('month').value
  const res   = await fetch(`${API}/analytics/summary?year=${year}&month=${month}`)
  const data  = await res.json()
  document.getElementById('val-income').textContent  = fmt(data.income)
  document.getElementById('val-expense').textContent = fmt(data.expense)
  document.getElementById('val-balance').textContent = fmt(data.balance)
}

// Загружаем список счетов при открытии вкладки Счета
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    if (tab.textContent === 'Счета') loadAccountsList()
  })
})