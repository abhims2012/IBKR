with open('template.html', 'r') as f:
    code = f.read()

# 1. Update Active Positions to show Name and Sector under the symbol
code = code.replace(
'''<h3 class="text-xl font-bold text-white mb-2">{{ pos.symbol }} <span class="text-xs font-normal ml-2 px-2 py-1 bg-slate-700 text-slate-300 rounded">{{ pos.currency }}</span></h3>''',
'''<div class="mb-2">
    <h3 class="text-xl font-bold text-white inline-block">{{ pos.symbol }}</h3>
    <span class="text-xs font-normal ml-2 px-2 py-1 bg-slate-700 text-slate-300 rounded">{{ pos.currency }}</span>
    <p class="text-xs text-slate-400 mt-1">{{ pos.name }} &bull; {{ pos.sector }}</p>
</div>'''
)

# 2. Update Trade History to show Name and Sector
code = code.replace(
'''<td class="px-6 py-4 font-bold text-white">{{ trade.symbol }}</td>''',
'''<td class="px-6 py-4">
    <div class="font-bold text-white">{{ trade.symbol }}</div>
    <div class="text-xs text-slate-400 truncate w-48">{{ trade.name }} ({{ trade.sector }})</div>
</td>'''
)

with open('template.html', 'w') as f:
    f.write(code)
