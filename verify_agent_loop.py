from modules.missions import run_mission

result = run_mission('127.0.0.1', include_osint=False)
print('success=', result['success'])
print('agent=', result['agent'])
