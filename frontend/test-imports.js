// Quick test to verify all imports work
console.log('Testing imports...')

// Test credentials
import('./src/lib/credentials.ts').then(module => {
  console.log('✅ credentials.ts exports:', Object.keys(module))
}).catch(err => {
  console.error('❌ credentials.ts error:', err.message)
})

// Test utils
import('./src/lib/utils.ts').then(module => {
  console.log('✅ utils.ts exports:', Object.keys(module))
}).catch(err => {
  console.error('❌ utils.ts error:', err.message)
})

// Test session
import('./src/lib/session.ts').then(module => {
  console.log('✅ session.ts exports:', Object.keys(module))
}).catch(err => {
  console.error('❌ session.ts error:', err.message)
})

console.log('Import test completed')