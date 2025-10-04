<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified principles: All principles replaced with new focus areas
- Added sections: Development Standards, Performance Requirements
- Removed sections: None (restructured existing sections)
- Templates requiring updates:
  ✅ spec-template.md (already aligned with new principles)
  ✅ plan-template.md (already aligned with new principles)  
  ✅ tasks-template.md (already aligned with new principles)
- Follow-up TODOs: None
-->

# PhoenixPrep Constitution

## Core Principles

### I. Code Quality Standards (NON-NEGOTIABLE)
Every component MUST follow consistent coding patterns, clear naming conventions, and maintainable architecture. Code MUST be self-documenting with meaningful variable names and minimal complexity. All code MUST pass automated linting and static analysis before deployment. Technical debt MUST be tracked and addressed within defined timeframes.

### II. Testing Standards (NON-NEGOTIABLE)
Test-Driven Development (TDD) is mandatory: Tests written → User approved → Tests fail → Then implement. All features MUST have comprehensive test coverage including unit, integration, and contract tests. Tests MUST be fast, reliable, and independent. Code coverage MUST exceed 80% for all critical paths.

### III. User Experience Consistency
All user interfaces MUST provide consistent interaction patterns, visual design, and feedback mechanisms. User workflows MUST be intuitive and follow established mental models. Error handling MUST be clear and actionable. Accessibility standards MUST be met for all user-facing components.

### IV. Performance Requirements
System performance MUST meet defined Service Level Objectives (SLOs) for response times, throughput, and resource utilization. Performance testing MUST be integrated into the development lifecycle. Critical user journeys MUST complete within acceptable time limits. Resource usage MUST be monitored and optimized continuously.

## Development Standards

### Code Review Requirements
All code changes MUST undergo peer review before merging. Reviewers MUST verify compliance with coding standards, test coverage, and performance requirements. Code reviews MUST focus on maintainability, security, and user experience impact.

### Quality Gates
Automated quality gates MUST block deployment if: code quality metrics decline, test coverage decreases, performance regressions occur, or security vulnerabilities are detected. Manual quality gates MUST verify user experience consistency and accessibility compliance.

## Performance Requirements

### Response Time Standards
- API endpoints: < 200ms p95 response time
- User interface interactions: < 100ms perceived latency  
- Data processing operations: < 500ms for standard operations
- File upload/processing: < 2 seconds for typical files

### Scalability Requirements
- System MUST handle concurrent user growth without degradation
- Database operations MUST scale with data volume increases
- Resource utilization MUST remain within defined thresholds
- Caching strategies MUST be implemented for frequently accessed data

## Governance

This constitution supersedes all other development practices and standards. Amendments require documentation of the change rationale, approval from project stakeholders, and a migration plan for existing code. All pull requests and code reviews MUST verify compliance with these principles. Complexity MUST be justified with clear business value. Use this document for runtime development guidance.

**Version**: 1.1.0 | **Ratified**: 2025-10-04 | **Last Amended**: 2025-10-04

---

## 中文总结

本宪法确立了凤凰备考项目的核心开发原则，重点关注：

**代码质量标准** - 强制要求一致的编码模式、清晰的命名规范和可维护的架构
**测试标准** - 强制采用测试驱动开发，要求全面的测试覆盖
**用户体验一致性** - 确保所有界面提供一致的交互模式和视觉设计
**性能要求** - 定义明确的性能指标和扩展性要求

所有开发活动必须遵守这些原则，确保项目质量和用户体验的持续提升。