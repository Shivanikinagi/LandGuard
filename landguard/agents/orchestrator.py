# """
# Workflow Orchestrator
# Coordinates the autonomous agents for complete document processing workflow
# """

# import asyncio
# import uuid
# from typing import List, Dict, Any
# from datetime import datetime

# from .base_agent import BaseAgent
# from .anomaly_detection_agent import AnomalyDetectionAgent
# from .compression_agent import CompressionAgent
# from .storage_agent import StorageAgent

# class WorkflowOrchestrator:
#     """Orchestrate the complete document processing workflow through autonomous agents"""
    
#     def __init__(self, encryption_password: str = "landguard_default"):
#         self.agents: List[BaseAgent] = [
#             AnomalyDetectionAgent(),
#             CompressionAgent(password=encryption_password),
#             StorageAgent()
#         ]
#         self.workflow_history = []
#         self.created_at = datetime.utcnow()
    
#     async def process_document(self, file_path: str) -> Dict[str, Any]:
#         """Process a document through the complete agentic workflow"""
#         workflow_id = str(uuid.uuid4())
#         workflow_start = asyncio.get_event_loop().time()
        
#         print(f"🚀 LANDGUARD AUTONOMOUS WORKFLOW")
#         print("=" * 40)
#         print(f"📄 Document: {file_path}")
#         print(f"🆔 Workflow ID: {workflow_id}")
#         print(f"⏱️  Start Time: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
#         # Step 1: Anomaly Detection
#         print(f"\n🕵️ STEP 1: FRAUD DETECTION")
#         print("-" * 25)
        
#         anomaly_agent = self._get_agent("anomaly_detector")
#         anomaly_task = {
#             "file_path": file_path
#         }
        
#         anomaly_result = await anomaly_agent.process(anomaly_task)
        
#         # Add success flag for consistency
#         anomaly_result["success"] = True
        
#         if anomaly_result.get("success"):
#             risk_score = anomaly_result.get("risk_score", 0)
#             anomalies = anomaly_result.get("anomalies", [])
            
#             print(f"✅ Analysis complete")
#             print(f"📊 Risk Score: {risk_score}/10")
#             print(f"⚠️  Anomalies: {len(anomalies)} detected")
            
#             if anomalies:
#                 for anomaly in anomalies[:3]:  # Show first 3 anomalies
#                     print(f"   • {anomaly.get('description', anomaly.get('type', 'Unknown anomaly'))}")
#                 if len(anomalies) > 3:
#                     print(f"   • ... and {len(anomalies) - 3} more")
#         else:
#             print(f"❌ Analysis failed: {anomaly_result.get('error')}")
            
#         # Step 2: Compression and Encryption
#         print(f"\n🔐 STEP 2: SECURITY PROCESSING")
#         print("-" * 25)
        
#         compression_agent = self._get_agent("compression_agent")
#         compression_task = {
#             "file_path": file_path,
#             "risk_score": anomaly_result.get("risk_score", 5.0),
#             "anomalies": anomaly_result.get("anomalies", [])
#         }
        
#         compression_result = await compression_agent.process(compression_task)
        
#         # Add success flag if missing
#         if "success" not in compression_result:
#             compression_result["success"] = compression_result.get("output_path") is not None
        
#         if compression_result.get("success"):
#             print(f"✅ Compression successful")
#             print(f"📁 Output: {compression_result.get('output_path')}")
#             print(f"📊 Ratio: {compression_result.get('compression_ratio', 1.0)}x")
#             print(f"🛡️ Method: {compression_result.get('method')}")
#         else:
#             print(f"❌ Compression failed: {compression_result.get('error')}")
            
#         # Step 3: Storage on IPFS and Blockchain
#         print(f"\n🌐 STEP 3: DISTRIBUTED STORAGE")
#         print("-" * 25)
        
#         storage_agent = self._get_agent("storage_agent")
#         storage_task = {
#             "file_path": compression_result.get("output_path", file_path),
#             "original_file": file_path
#         }
        
#         storage_result = await storage_agent.process(storage_task)
        
#         # Print storage results
#         ipfs_result = storage_result.get("ipfs", {})
#         blockchain_result = storage_result.get("blockchain", {})
        
#         if ipfs_result.get("success"):
#             print(f"✅ IPFS Upload Successful")
#             print(f"🔗 CID: {ipfs_result.get('cid')}")
#             print(f"🌐 Nodes: {ipfs_result.get('nodes')} nodes")
#         else:
#             print(f"❌ IPFS Upload Failed: {ipfs_result.get('error')}")
            
#         if blockchain_result.get("success"):
#             print(f"✅ Blockchain Registration Successful")
#             print(f"🔗 TX: {blockchain_result.get('transaction_hash')[:16]}...")
#             print(f"⛓️ Network: {blockchain_result.get('network')}")
            
#             # Show explorer link for real transactions
#             method = blockchain_result.get('method', '')
#             if 'REAL' in method.upper():
#                 tx_hash = blockchain_result.get('transaction_hash')
#                 if tx_hash.startswith('0x'):
#                     # Use the polygon handler's explorer URL method
#                     try:
#                         from ..Blockchain.blockchain.polygon_handler import PolygonHandler
#                         handler = PolygonHandler()
#                         explorer_url = handler.get_explorer_url(tx_hash)
#                         print(f"🔍 Explorer: {explorer_url}")
#                     except:
#                         # Fallback to direct URL construction
#                         explorer_url = f"https://mumbai.polygonscan.com/tx/{tx_hash}"
#                         print(f"🔍 Explorer: {explorer_url}")
#         else:
#             print(f"❌ Blockchain Registration Failed: {blockchain_result.get('error')}")
            
#         # Compile final results
#         workflow_duration = asyncio.get_event_loop().time() - workflow_start
#         final_result = {
#             "workflow_id": workflow_id,
#             "file_path": file_path,
#             "anomaly_detection": anomaly_result,
#             "compression": compression_result,
#             "storage": storage_result,
#             "duration_seconds": round(workflow_duration, 2),
#             "timestamp": asyncio.get_event_loop().time()
#         }
        
#         self.workflow_history.append(final_result)
        
#         # Print final summary
#         print(f"\n✅ WORKFLOW COMPLETE")
#         print("=" * 20)
#         print(f"⏱️ Duration: {final_result['duration_seconds']}s")
        
#         if ipfs_result.get("success") and blockchain_result.get("success"):
#             print(f"🔒 Document secured on blockchain")
#             print(f"🆔 Verification CID: {ipfs_result.get('cid')}")
#             print(f"📝 TX: {blockchain_result.get('transaction_hash')}")
            
#             # Show explorer link for real transactions
#             method = blockchain_result.get('method', '')
#             if 'REAL' in method.upper():
#                 tx_hash = blockchain_result.get('transaction_hash')
#                 if tx_hash.startswith('0x'):
#                     # Use the polygon handler's explorer URL method
#                     try:
#                         from ..Blockchain.blockchain.polygon_handler import PolygonHandler
#                         handler = PolygonHandler()
#                         explorer_url = handler.get_explorer_url(tx_hash)
#                         print(f"🌐 View on Explorer: {explorer_url}")
#                     except:
#                         # Fallback to direct URL construction
#                         explorer_url = f"https://mumbai.polygonscan.com/tx/{tx_hash}"
#                         print(f"🌐 View on Explorer: {explorer_url}")
            
#         print(f"\n🔍 VERIFICATION COMMAND:")
#         print(f"landguard-agents verify {ipfs_result.get('cid', 'CID_NOT_AVAILABLE')}")
        
#         return final_result
        
#     def _get_agent(self, agent_name: str) -> BaseAgent:
#         """Get agent by name"""
#         for agent in self.agents:
#             if agent.name == agent_name:
#                 return agent
#         raise ValueError(f"Agent {agent_name} not found")
        
#     def get_agent_status(self) -> Dict[str, Any]:
#         """Get status of all agents"""
#         return {
#             agent.name: agent.get_status() for agent in self.agents
#         }
        
#     def verify_document(self, cid: str) -> Dict[str, Any]:
#         """Verify a document using the storage agent"""
#         storage_agent = self._get_agent("storage_agent")
#         return storage_agent.verify_document(cid)

# # Convenience function for easy use
# async def process_land_document(file_path: str) -> Dict[str, Any]:
#     """Convenience function to process a land document"""
#     orchestrator = WorkflowOrchestrator()
#     return await orchestrator.process_document(file_path)


"""
Workflow Orchestrator
Coordinates the autonomous agents for complete document processing workflow.

This version implements an *interactive* agentic flow:
1. Run anomaly / fraud analysis and show results to the user.
2. Ask for permission (yes/no) to encrypt the data.
3. Ask for permission (yes/no) to compress the data.
4. Proceed with .ppc creation, IPFS upload, optional blockchain registration.
"""

import asyncio
import os
import sys
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, time

from .base_agent import BaseAgent
from .anomaly_detection_agent import AnomalyDetectionAgent
from .compression_agent import CompressionAgent
from .storage_agent import StorageAgent


class WorkflowOrchestrator:
    """Orchestrate the complete document processing workflow through autonomous agents"""

    def __init__(self, encryption_password: str = "landguard_default", interactive: bool = True):
        self.agents: List[BaseAgent] = [
            AnomalyDetectionAgent(),
            CompressionAgent(password=encryption_password),
            StorageAgent(),
        ]
        self.workflow_history: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()
        self.interactive = interactive
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0

    # -------------------------------------------------------------------------
    # Visual Helper Methods
    # -------------------------------------------------------------------------
    async def _animate_step(self, duration: float = 0.5):
        """Smooth animation with spinner"""
        steps = int(duration * 20)
        for _ in range(steps):
            await asyncio.sleep(duration / steps)

    async def _step(self, number: int, title: str):
        """Display step header with animation"""
        await asyncio.sleep(0.2)
        print(f"\n  ✦ STEP {number}: {title}")
        print(f"  {'─' * (len(title) + 14)}")
        await asyncio.sleep(0.15)

    def _print_status(self, icon: str, message: str, detail: str = ""):
        """Print a status line with consistent formatting"""
        if detail:
            print(f"  {icon}  {message}")
            print(f"     └─ {detail}")
        else:
            print(f"  {icon}  {message}")

    def _print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n  ╭─ {title}")

    def _print_item(self, label: str, value: Any, indent: int = 1):
        """Print a labeled item with smart truncation"""
        prefix = "  │   " if indent == 1 else "      "
        value_str = str(value)
        # Truncate long values intelligently
        if len(value_str) > 60:
            value_str = value_str[:57] + "…"
        print(f"{prefix}• {label}: {value_str}")

    def _print_section_end(self):
        """Print section footer"""
        print(f"  ╰─────────────────")

    async def _delayed_print(self, message: str, delay: float = 0.1):
        """Print message with smooth delay"""
        await asyncio.sleep(delay)
        print(message)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    async def process_document(self, file_path: str, *, encrypt=None, compress=None, enable_blockchain=None):
        """Main workflow entry point with enhanced visuals"""

        workflow_id = str(uuid.uuid4())
        
        # Title banner
        print("\n" + "  " + "╭" + "─" * 50 + "╮")
        print("  " + "│" + "  🚀  LANDGUARD AUTONOMOUS WORKFLOW INITIALIZED  " + "│")
        print("  " + "╰" + "─" * 50 + "╯")
        
        print(f"\n  📄  File Path:    {os.path.basename(file_path)}")
        print(f"  🔑  Workflow ID:  {workflow_id[:12]}…")
        
        await self._animate_step(0.4)

        # STEP 1 — LOAD + VALIDATION
        await self._step(1, "Loading & Validating Document")
        self._print_status("📖", "Reading file into workflow…")

        if not os.path.exists(file_path):
            self._print_status("❌", "File not found — stopping workflow")
            return

        await self._animate_step(0.3)
        self._print_status("✓", "Document loaded successfully")

        # STEP 2 — ANOMALY CHECK
        await self._step(2, "Fraud Detection & Risk Analysis")
        self._print_status("🔍", "Analyzing document for anomalies…")
        
        anomaly_agent = self._get_agent("anomaly_detector")
        anomaly_res = await anomaly_agent.process({"file_path": file_path})
        
        await self._animate_step(0.2)
        
        risk_score = anomaly_res["risk_score"]
        risk_icon = "🟢" if risk_score < 3 else "🟡" if risk_score < 6 else "🔴"
        
        self._print_status("✓", f"Analysis complete — Risk Score: {risk_icon} {risk_score}/10")
        
        if anomaly_res["anomalies"]:
            self._print_section("Detected Issues")
            for i, a in enumerate(anomaly_res["anomalies"][:4], 1):
                severity_icon = "⚠️ " if a.get('severity') == 'HIGH' else "ℹ️ " if a.get('severity') == 'LOW' else "⚡"
                self._print_item(
                    f"{severity_icon}{a['type']}", 
                    a['description'][:50] + "…" if len(a['description']) > 50 else a['description']
                )
            if len(anomaly_res["anomalies"]) > 4:
                print(f"  │   … and {len(anomaly_res['anomalies']) - 4} more issues detected")
            self._print_section_end()

        # STEP 3 — USER PERMISSION
        await self._step(3, "Requesting Security Permissions")
        
        encrypt = encrypt if encrypt is not None else self._ask_yes_no("🔐 Encrypt file?")
        compress = compress if compress is not None else self._ask_yes_no("🗜  Compress file?")
        enable_blockchain = enable_blockchain if enable_blockchain is not None else self._ask_yes_no("⛓  Store on blockchain?")

        await self._animate_step(0.2)
        
        self._print_section("Security Configuration")
        self._print_item("Encryption", "✓ ON" if encrypt else "✗ OFF")
        self._print_item("Compression", "✓ ON" if compress else "✗ OFF")
        self._print_item("Blockchain", "✓ ON" if enable_blockchain else "✗ OFF")
        self._print_section_end()

        # STEP 4 — COMPRESSION/ENCRYPTION
        await self._step(4, "Creating Secured PPC Package")
        self._print_status("📦", "Building encrypted container…")
        
        compression_agent = self._get_agent("compression_agent")
        comp_res = await compression_agent.process({"file_path": file_path, "encrypt": encrypt, "compress": compress})
        
        await self._animate_step(0.25)
        
        output_filename = os.path.basename(comp_res['output_path'])
        self._print_status("✓", "PPC package created", f"File: {output_filename}")

        # STEP 5 — IPFS STORAGE
        await self._step(5, "Uploading to Distributed Storage")
        self._print_status("🌐", "Publishing to IPFS network…")
        
        storage_agent = self._get_agent("storage_agent")
        store_res = await storage_agent.process({"file_path": comp_res['output_path'], "enable_blockchain": enable_blockchain})

        await self._animate_step(0.3)
        
        if store_res["ipfs"]["success"]:
            self._print_status("✓", "IPFS upload successful", f"CID: {store_res['ipfs']['cid'][:20]}…")
        else:
            self._print_status("❌", "IPFS upload failed")

        # STEP 6 — BLOCKCHAIN REGISTRATION
        await self._step(6, "Blockchain Verification")
        
        if enable_blockchain and store_res["blockchain"]["success"]:
            self._print_status("⛓", "Blockchain registration complete", 
                             f"TX: {store_res['blockchain']['transaction_hash'][:16]}…")
            await self._animate_step(0.25)
        else:
            self._print_status("ℹ️ ", "Blockchain storage disabled")

        # FINAL STATUS
        await self._step(7, "Finalizing & Audit Trail")
        await self._animate_step(0.3)
        
        # Success banner
        print("\n" + "  " + "╭" + "─" * 50 + "╮")
        print("  " + "│" + "  ✓  WORKFLOW COMPLETED SUCCESSFULLY              " + "│")
        print("  " + "╰" + "─" * 50 + "╯")
        
        # Verification info
        cid = store_res['ipfs']['cid']
        print(f"\n  🔗  Document CID:  {cid}")
        print(f"  📋  Verify using:  landguard-agents verify {cid[:20]}…")
        
        # Show summary stats if available
        if comp_res.get('original_size'):
            original_size = comp_res.get('original_size', 0)
            compressed_size = comp_res.get('compressed_size', 0)
            ratio = comp_res.get('compression_ratio', 1.0)
            print(f"  📊  Statistics:")
            print(f"       Original: {self._format_bytes(original_size)}")
            print(f"       Encrypted: {self._format_bytes(compressed_size)}")
            print(f"       Ratio: {ratio}x")
        
        print()
        
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}TB"

        
    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _get_agent(self, agent_name: str) -> BaseAgent:
        """Get agent by name"""
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        raise ValueError(f"Agent {agent_name} not found")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {agent.name: agent.get_status() for agent in self.agents}

    def verify_document(self, cid: str) -> Dict[str, Any]:
        """Verify a document using the storage agent"""
        storage_agent = self._get_agent("storage_agent")
        return storage_agent.verify_document(cid)

    @staticmethod
    def _ask_yes_no(prompt: str, default: bool = True) -> bool:
        """Simple blocking yes/no prompt used in CLI workflows.

        This intentionally uses input() and is meant for terminal / interactive
        usage only.
        """
        default_str = "Y/n" if default else "y/N"
        while True:
            answer = input(f"{prompt} [{default_str}] ").strip().lower()
            if not answer:
                return default
            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False
            print("Please answer 'y' or 'n'.")


# Convenience wrappers --------------------------------------------------------


async def process_land_document(file_path: str, password: str = "landguard_default") -> Dict[str, Any]:
    """Backwards-compatible helper to process a land document."""
    orchestrator = WorkflowOrchestrator(encryption_password=password, interactive=False)
    return await orchestrator.process_document(file_path)


async def process_document_agentic(
    file_path: str,
    password: str = "landguard_default",
    *,
    interactive: bool = True,
) -> Dict[str, Any]:
    """Entry point used by the CLI (landguard-agents).

    This will:
    - run anomaly analysis
    - ask user for encryption / compression / blockchain choices
    - run the full workflow accordingly
    """
    orchestrator = WorkflowOrchestrator(encryption_password=password, interactive=interactive)
    return await orchestrator.process_document(file_path)