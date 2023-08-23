## Introduce
지극히 개인적인 지리정보 관리 및 검색을 위한 패키지


## Baseline
- Geohash 기반의 공간정보들을 공간연산하기 위한 
RTree 등을 기초로 함.
- 각 요소들의 검증은 pydantic v2로 진행함.
- 지금 작성되어있는 요소들을 이 패키지로 이전하며, 동일한 기능이 되도록 유닛테스트 실시
- 핵심은 crs:4326 등의 좌표요소들의 객체로 변환을 쉽게 하는 것
