import { describe, it, expect } from 'bun:test'
import { appRouter } from '../../src/routers'
import type { Context } from '../../src/context'

describe('Video Router', () => {
  it('should have video procedures', () => {
    // Just check that the router has the expected procedures
    expect(appRouter._def.procedures).toHaveProperty('video')
    expect(appRouter._def.procedures.video._def.procedures).toHaveProperty('upload')
    expect(appRouter._def.procedures.video._def.procedures).toHaveProperty('list')
    expect(appRouter._def.procedures.video._def.procedures).toHaveProperty('getById')
    expect(appRouter._def.procedures.video._def.procedures).toHaveProperty('delete')
  })

  it('should have jobs procedures', () => {
    expect(appRouter._def.procedures).toHaveProperty('jobs')
    expect(appRouter._def.procedures.jobs._def.procedures).toHaveProperty('list')
    expect(appRouter._def.procedures.jobs._def.procedures).toHaveProperty('getById')
    expect(appRouter._def.procedures.jobs._def.procedures).toHaveProperty('cancel')
  })

  it('should have chat procedures', () => {
    expect(appRouter._def.procedures).toHaveProperty('chat')
    expect(appRouter._def.procedures.chat._def.procedures).toHaveProperty('create')
    expect(appRouter._def.procedures.chat._def.procedures).toHaveProperty('sendMessage')
  })
})