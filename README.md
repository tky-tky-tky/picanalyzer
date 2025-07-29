# Picanalyzer

Django学習の過程で作成した、画像分類Webアプリケーションです。  
アップロードした画像をAIモデルで解析し、ラベルを自動で分類・表示します。
<img width="1257" height="815" alt="image" src="https://github.com/user-attachments/assets/7e232bdd-e9d8-41fb-8169-50a4da03dd54" />

<img width="1256" height="745" alt="image" src="https://github.com/user-attachments/assets/62519a90-99ce-486f-aca5-354a1620a4a3" />



---

## 🔍 主な機能

- 画像アップロード機能（複数形式に対応）
- 学習済みAIモデルを用いた画像分類
- 解析結果のラベル表示と信頼度（reliability）表示
- 解析結果の履歴管理（データベース連携）
- 管理画面（ユーザー・画像）
- PC／スマホ向けのレスポンシブUI
- Celery + SQS による非同期画像解析

---

### 🗂️ テーブル設計（ER図）
<img width="1061" height="265" alt="画像解析テーブル課題 drawio(1)" src="https://github.com/user-attachments/assets/b9f7e4d4-8927-420a-b457-d64f3cb1bdd6" />

---

## 📸 スクリーンショット
<img width="1257" height="815" alt="image" src="https://github.com/user-attachments/assets/7e232bdd-e9d8-41fb-8169-50a4da03dd54" />

<img width="1256" height="745" alt="image" src="https://github.com/user-attachments/assets/62519a90-99ce-486f-aca5-354a1620a4a3" />

