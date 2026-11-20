# 기술 아키텍처 · 인프라 도식화 가이드 (AWS 스타일)

사용자가 특히 좋아하는 산출물 요소. 원본 레퍼런스: `works/078.../02_아너파라다이스_사업개요_v0.8_고객용.html`. 도식 CSS는 `template/diagrams.css`에 추출되어 있다. builder는 인프라/아키텍처 섹션을 만들 때 이 가이드를 따른다.

## ★ AS-IS / TO-BE 원칙 (인프라 도식의 핵심 규율)
- **AS-IS(현행)가 고객 제공 구성도면 → `figure`로 원본 그대로 수록**(변형·재작도 금지). `aws-*` 그리드는 논리 구성용이라 온프레미스 물리 토폴로지(L4·서버명·연결선·이중화 쌍)를 못 담는다. 자료 없을 때만 텍스트 기반 개략 재현(+"재구성·추정").
- **TO-BE(제안)는 AS-IS의 delta로 도출** — 일반 모범 구성도를 갖다 붙이지 마라. AS-IS 각 요소를 **유지/변경/신규/제거**로 분류하고 각 변경에 **근거(RFP 요구·현행 한계)**를 단다. 현행 필수 요소(이중화·환경분리·연계 시스템·IDC·핵심 장비)를 **근거 없이 없애지 마라**(사고: TO-BE에서 연계 4종 누락). 노드 `meta`에 상태("유지·이중화"·"신규(RFP:GEO/SEO)"·"현대화 JDK17") 표기. AS-IS→TO-BE **delta 표(유지/변경/신규/제거+근거)**를 함께 둔다. **RFP에 인프라 요구가 없고 현행 자료도 없을 때만** 일반 권장 구성도(개략·"추정") 허용.

## 두 가지 도식
1. **개념도 (허브-위성 방사형, `.eco-*`)** — "통합 생태계 한 장으로 보기"처럼 중심 + 주변 행위자/시스템을 원형 배치. 사업/생태계 개요에 사용. CSS: `.eco-hub`/`.eco-svg`(연결선)/`.eco-center`/`.eco-sat`(`data-i="0~9"`로 위치 지정)/`.eco-group-label`/`.eco-legend`.
2. **AWS 인프라 구성도 (`.infra-diagram`/`.aws-*`)** — AWS 공식 아이콘으로 VPC/계정/외부 경계를 박스로, 서비스를 아이콘 그리드로 배치. CSS: `.infra-diagram`/`.aws-flow`/`.aws-row`/`.aws-col`/`.aws-box`(`.aws-account` 핑크 경계 / `.aws-external` 외부)/`.aws-box-label`(`.ico`)/`.aws-svc-grid`/`.aws-svc`(`.ico`/`.name`/`.meta`)/`.aws-legend`/`.aws-flow-list`.

## AWS 공식 아이콘 소스 (핵심)
PlantUML용 AWS 공식 아이콘 PNG를 GitHub raw로 직접 참조한다(안정 URL):
```
https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/{카테고리}/{서비스}.png
```
`<img>`로 `.aws-svc .ico`에 넣는다. 자주 쓰는 매핑:

| 서비스 | 경로 |
|--------|------|
| 사용자 | `General/Users.png` |
| Route 53 | `NetworkingContentDelivery/Route53.png` |
| CloudFront | `NetworkingContentDelivery/CloudFront.png` |
| ALB | `NetworkingContentDelivery/ElasticLoadBalancingApplicationLoadBalancer.png` |
| API Gateway | `NetworkingContentDelivery/APIGateway.png` |
| NAT Gateway | `NetworkingContentDelivery/VPCNATGateway.png` |
| Transit Gateway | `NetworkingContentDelivery/TransitGateway.png` |
| WAF | `SecurityIdentityCompliance/WAF.png` |
| Cognito | `SecurityIdentityCompliance/Cognito.png` |
| KMS | `SecurityIdentityCompliance/KeyManagementService.png` |
| Secrets Manager | `SecurityIdentityCompliance/SecretsManager.png` |
| GuardDuty | `SecurityIdentityCompliance/GuardDuty.png` |
| ECS | `Containers/ElasticContainerService.png` |
| Lambda | `Compute/Lambda.png` |
| Aurora PostgreSQL | `Database/AuroraPostgreSQLInstance.png` |
| DynamoDB | `Database/DynamoDB.png` |
| ElastiCache(Redis) | `Database/ElastiCacheElastiCacheforRedis.png` |
| OpenSearch | `Analytics/OpenSearchService.png` |
| Redshift | `Analytics/Redshift.png` |
| S3 | `Storage/SimpleStorageService.png` |
| CloudWatch | `ManagementGovernance/CloudWatch.png` |
| CloudTrail | `ManagementGovernance/CloudTrail.png` |
| SES | `BusinessApplications/SimpleEmailService.png` |
| SNS | `ApplicationIntegration/SimpleNotificationService.png` |

> 다른 서비스는 같은 repo의 `dist/` 트리에서 `{카테고리}/{서비스}.png`를 찾는다(카테고리명은 AWS 콘솔 분류와 동일: Compute/Database/Networking…). 불확실하면 firecrawl/web으로 repo 트리를 확인.

## self-contained 트레이드오프 (반드시 안내)
- AWS 아이콘은 **외부 PNG**라 렌더에 인터넷이 필요하다. 078은 외부 참조 방식을 썼고 사용자가 이를 선호함 → **기본값: 외부 URL**.
- 완전 오프라인 전달이 필요하면 아이콘을 로컬에 내려받아 상대경로로 교체(또는 base64 인라인). builder는 사용자가 "오프라인/단일파일 완전체"를 요구할 때만 로컬화한다.

## 추가 :root 변수 (diagrams.css 의존)
개념도/일부 박스가 다음 색을 참조한다. builder는 `<style>` :root에 추가:
```
--paradise-black:#0a0a0a; --paradise-dark:#1a1a1a; --paradise-deep:#2a2114;
--gold-light:#d4b87c; --gold-pale:#ebd8a7;
```
(프로젝트 톤에 맞게 조정 가능. AWS 계정 경계 핑크 #E7157B는 AWS 표준이므로 유지 권장.)

## builder 작업 절차 (인프라 섹션)
1. architect의 아키텍처 설계(계층/서비스 목록)를 받는다.
2. 서비스 → 위 아이콘 매핑으로 `<img>` URL 결정(목록에 없으면 repo에서 탐색).
3. `template/diagrams.css`를 `<style>`에 인라인 + 필요한 :root 변수 추가.
4. `.infra-diagram` 안에 계정/외부 경계 박스(`.aws-box`) → 계층별 `.aws-svc-grid` → 서비스 `.aws-svc` 배치.
5. 데이터 흐름은 `.aws-flow-list`(번호 단계)로 텍스트 병기.
6. 개념도가 필요하면 `.eco-hub` 방사형으로 생태계 한 장 요약.
