"""
Convenience entry point to run RetailRec India locally in VS Code or Terminal.
Usage:
    python run.py
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  🚀 Starting RetailRec India Recommendation Engine")
    print("=" * 65)
    print("  🌐 Web Dashboard:    http://127.0.0.1:8000")
    print("  🎯 Recommendations:  http://127.0.0.1:8000/recommendations")
    print("  📚 API Documentation: http://127.0.0.1:8000/docs")
    print("  🩺 Health Check:     http://127.0.0.1:8000/health")
    print("=" * 65 + "\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
